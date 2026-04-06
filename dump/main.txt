#!/usr/bin/env python3
"""
DevOps Transformation Platform - Main Entry Point
==================================================

Main entry point for running the DevOps Transformation Platform.

This script provides commands for:
    - Weekly data refresh
    - Database setup
    - Running tests
    - Launching the dashboard

Usage:
    python main.py refresh     # Run weekly data refresh
    python main.py setup       # Initialize database
    python main.py dashboard   # Launch Streamlit dashboard
    python main.py test        # Run test suite

Author: DevOps Transformation Team
"""

import sys
import os
import logging
import argparse
from datetime import datetime, timedelta

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.config import Config, setup_logging
from src.data.database import Database
from src.data.registry import RegistryLoader
from src.api.datasight import DataSightClient
from src.api.github import GitHubClient
from src.api.llm import LLMClient
from src.core.calculator import MetricsCalculator
from src.core.badges import BadgeEngine
from src.core.hygiene_checker import HygieneChecker
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


def setup_database(config: Config):
    """
    Initialize the database with required tables.
    
    Args:
        config: Application configuration.
    """
    logger.info("Setting up database...")
    
    db = Database(config.db_path)
    stats = db.get_statistics()
    
    logger.info(f"Database initialized at: {config.db_path}")
    logger.info(f"  Total pods: {stats['total_pods']}")
    logger.info(f"  Total metrics records: {stats['total_metrics_records']}")
    
    print("\n✅ Database setup complete!")
    print(f"   Path: {config.db_path}")


def generate_repo_documentation(
    github_client: GitHubClient,
    llm_client: LLMClient,
    repo_full_name: str,
    full_url: str,
    output_dir: Path
) -> bool:
    """
    Generate documentation for a single repository using LLM.
    
    Args:
        github_client: Initialized GitHub client
        llm_client: Initialized LLM client
        repo_full_name: Full repo name (org/repo)
        full_url: Full URL for enterprise GitHub
        output_dir: Directory to save documentation
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"[DOC-GEN] Starting documentation generation for: {repo_full_name}")
    
    try:
        # Determine API base for enterprise GitHub
        api_base = github_client._get_api_url(repo_full_name, full_url)
        logger.debug(f"[DOC-GEN] Using API base: {api_base}")
        
        # Get repository info
        logger.info(f"[DOC-GEN] Fetching repository metadata...")
        repo_info = github_client.get_repository_info(repo_full_name)
        if not repo_info:
            logger.warning(f"[DOC-GEN] Could not fetch repo info, using defaults")
            repo_info = {'name': repo_full_name.split('/')[-1], 'description': None}
        
        # Get repository tree
        logger.info(f"[DOC-GEN] Fetching repository file tree...")
        default_branch = repo_info.get('default_branch', 'main')
        tree_paths = github_client.get_repository_tree(repo_full_name, default_branch)
        logger.info(f"[DOC-GEN] Found {len(tree_paths)} files in repository")
        
        # Collect evidence files
        logger.info(f"[DOC-GEN] Collecting evidence files (README, package.json, etc.)...")
        evidence_files = github_client.collect_evidence_files(
            repo_full_name, 
            default_branch,
            max_files=10
        )
        logger.info(f"[DOC-GEN] Collected {len(evidence_files)} evidence files:")
        for ef in evidence_files:
            logger.debug(f"[DOC-GEN]   - {ef['path']}")
        
        # Analyze with LLM
        logger.info(f"[DOC-GEN] Sending to LLM for analysis...")
        analysis = llm_client.analyze_repository(
            repo_full_name,
            repo_info,
            tree_paths,
            evidence_files
        )
        
        if not analysis:
            logger.error(f"[DOC-GEN] LLM analysis returned empty result")
            return False
        
        logger.info(f"[DOC-GEN] LLM analysis complete!")
        logger.info(f"[DOC-GEN]   Summary: {analysis.get('summary', 'N/A')[:80]}...")
        logger.info(f"[DOC-GEN]   Components: {len(analysis.get('key_components', []))}")
        logger.info(f"[DOC-GEN]   Tech stack: {len(analysis.get('tech_stack', []))}")
        
        # Generate documentation markdown
        logger.info(f"[DOC-GEN] Generating markdown documentation...")
        doc_content = llm_client.generate_documentation(repo_full_name, analysis)
        
        # Save documentation
        repo_name_safe = repo_full_name.replace('/', '_')
        output_file = output_dir / f"{repo_name_safe}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(doc_content)
        
        logger.info(f"[DOC-GEN] ✓ Documentation saved to: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"[DOC-GEN] ✗ Error generating docs for {repo_full_name}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def run_weekly_refresh(config: Config, generate_docs: bool = False):
    """
    Run weekly data refresh to collect metrics.
    
    Args:
        config: Application configuration.
        generate_docs: If True, generate documentation for repos after scoring.
    """
    logger.info("=" * 60)
    logger.info("Starting Weekly Data Refresh")
    logger.info("=" * 60)
    
    # Check if docs generation is enabled via env var
    if os.getenv('ENABLE_DOCS_GENERATION', '').lower() in ('true', '1', 'yes'):
        generate_docs = True
        logger.info("Documentation generation ENABLED via ENABLE_DOCS_GENERATION env var")
    
    # Validate configuration
    if not config.datasight_token:
        logger.error("DATASIGHT_BEARER_TOKEN not configured")
        print("\n❌ Error: DATASIGHT_BEARER_TOKEN environment variable not set")
        print("   Please set it in your .env file or environment")
        return
    
    # Initialize components
    db = Database(config.db_path)
    registry = RegistryLoader(config.registry_dir)
    datasight = DataSightClient(config.datasight_token)
    calculator = MetricsCalculator()
    badge_engine = BadgeEngine()
    
    # Initialize GitHub client and hygiene checker if token available
    github_client = None
    hygiene_checker = None
    if config.github_token:
        github_client = GitHubClient(config.github_token)
        hygiene_checker = HygieneChecker(github_client, config.hygiene_config)
        logger.info("GitHub hygiene checking ENABLED (6 comprehensive checks)")
    else:
        logger.warning("No GITHUB_TOKEN - hygiene checks will be skipped")
    
    # Initialize LLM client if docs generation enabled
    llm_client = None
    if generate_docs:
        if os.getenv('AM_TOKEN'):
            llm_client = LLMClient()
            logger.info("LLM documentation generation ENABLED")
        else:
            logger.warning("No AM_TOKEN - documentation generation will be skipped")
            generate_docs = False
    
    # Load applications from registry
    apps = registry.load_all_apps()
    logger.info(f"Loaded {len(apps)} applications from registry")
    
    if not apps:
        logger.warning("No applications found in registry")
        print("\n⚠️  No applications found in registry directory")
        print(f"   Registry path: {config.registry_dir}")
        return
    
    # Calculate date range (last 30 days)
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)
    week_date = to_date.strftime('%Y-%m-%d')
    
    logger.info(f"Fetching metrics from {from_date.strftime('%Y-%m')} to {to_date.strftime('%Y-%m')}")
    
    # Process each application
    processed = 0
    failed = 0
    
    for app in apps:
        try:
            logger.info(f"\nProcessing: {app.app_name} ({app.app_id})")
            
            # Fetch DataSight metrics
            metrics = datasight.get_all_metrics(
                app.pod_name,
                app.pod_level,
                from_date,
                to_date
            )
            
            # Add app configuration to metrics
            metrics.update(app.config)
            
            # Calculate Git hygiene using comprehensive checker
            if hygiene_checker and app.repos:
                total_hygiene = 0
                total_critical = 0
                total_warnings = 0
                
                logger.info(f"  Running comprehensive hygiene checks for {len(app.repos)} repositories")
                for repo in app.repos:
                    try:
                        # Parse owner/repo from full_name
                        parts = repo.full_name.split('/')
                        if len(parts) != 2:
                            logger.warning(f"  Invalid repo format: {repo.full_name}")
                            continue
                        
                        owner, repo_name = parts
                        
                        # Run all 6 hygiene checks
                        result = hygiene_checker.check_repo(owner, repo_name, full_url=repo.full_url)
                        
                        score = result.score if result.score is not None else 0
                        total_hygiene += score
                        total_critical += result.critical_count
                        total_warnings += result.warning_count
                        
                        # Count violations by check type
                        check_counts = {}
                        for v in result.violations:
                            check_counts[v.check] = check_counts.get(v.check, 0) + 1
                        
                        # Build minimal violation summary
                        violation_parts = []
                        for check, count in sorted(check_counts.items()):
                            if check != "api_error":
                                violation_parts.append(f"{check}:{count}")
                        violation_summary = " | ".join(violation_parts) if violation_parts else "none"
                        
                        status = "✓" if result.passed else "✗"
                        logger.info(f"    {status} {repo.full_name}: {score}/100 [{violation_summary}]")
                            
                    except Exception as e:
                        logger.warning(f"  Hygiene check failed for {repo.full_name}: {e}")
                
                if app.repos:
                    metrics['git_hygiene_score'] = total_hygiene / len(app.repos)
                    metrics['git_hygiene_violations_critical'] = total_critical
                    metrics['git_hygiene_violations_warnings'] = total_warnings
                    logger.info(f"  Average hygiene score: {metrics['git_hygiene_score']:.1f}/100")
            
            # Calculate pillar scores
            scores = calculator.calculate_all_scores(metrics)
            metrics.update(scores)
            
            # Compute badges
            badges = badge_engine.compute_badges(scores)
            
            # Upsert pod info
            db.upsert_pod(
                pod_id=app.app_id,
                pod_name=app.app_name,
                stack=app.stack,
                business_unit=app.business_unit,
                tier=app.tier
            )
            
            # Insert weekly metrics
            metrics['pod_id'] = app.app_id
            metrics['week_date'] = week_date
            db.insert_weekly_metrics(metrics)
            
            logger.info(f"  ✓ DPI: {scores['dpi']:.1f} | Badges: {len(badges)}")
            processed += 1
            
        except Exception as e:
            logger.error(f"  ✗ Failed to process {app.app_name}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            failed += 1
    
    # Summary for metrics collection
    logger.info("\n" + "=" * 60)
    logger.info("Metrics Collection Complete")
    logger.info("=" * 60)
    logger.info(f"  Processed: {processed}")
    logger.info(f"  Failed: {failed}")
    
    # Get updated stats
    stats = db.get_statistics()
    logger.info(f"  Average DPI: {stats['average_dpi']}")
    
    # ========================================
    # DOCUMENTATION GENERATION PHASE
    # ========================================
    docs_generated = 0
    docs_failed = 0
    
    if generate_docs and llm_client and github_client:
        logger.info("\n" + "=" * 60)
        logger.info("Starting Documentation Generation")
        logger.info("=" * 60)
        
        # Output directory for generated docs
        docs_output_dir = Path(PROJECT_ROOT) / "docs" / "generated"
        logger.info(f"Output directory: {docs_output_dir}")
        
        for app in apps:
            if not app.repos:
                logger.info(f"\n[DOC-GEN] Skipping {app.app_name} - no repos configured")
                continue
            
            logger.info(f"\n[DOC-GEN] Processing app: {app.app_name} ({len(app.repos)} repos)")
            
            # Create app-specific output directory
            app_output_dir = docs_output_dir / app.app_name
            
            for repo in app.repos:
                logger.info(f"\n[DOC-GEN] --- Repo: {repo.full_name} ---")
                
                success = generate_repo_documentation(
                    github_client,
                    llm_client,
                    repo.full_name,
                    repo.full_url,
                    app_output_dir
                )
                
                if success:
                    docs_generated += 1
                else:
                    docs_failed += 1
        
        # Documentation summary
        logger.info("\n" + "=" * 60)
        logger.info("Documentation Generation Complete")
        logger.info("=" * 60)
        logger.info(f"  Generated: {docs_generated}")
        logger.info(f"  Failed: {docs_failed}")
        logger.info(f"  Output: {docs_output_dir}")
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("Weekly Refresh Complete")
    logger.info("=" * 60)
    
    print(f"\n✅ Weekly refresh complete!")
    print(f"   Processed: {processed} applications")
    print(f"   Failed: {failed}")
    print(f"   Average DPI: {stats['average_dpi']}")
    
    if generate_docs:
        print(f"\n📄 Documentation generation:")
        print(f"   Generated: {docs_generated}")
        print(f"   Failed: {docs_failed}")
        print(f"   Output: docs/generated/")


def launch_dashboard():
    """Launch the Streamlit dashboard."""
    import subprocess
    
    dashboard_path = os.path.join(PROJECT_ROOT, "dashboard.py")
    
    if not os.path.exists(dashboard_path):
        # Fall back to app.py
        dashboard_path = os.path.join(PROJECT_ROOT, "app.py")
    
    print("🚀 Launching dashboard...")
    print("   Access at: http://localhost:8501")
    print("   Press Ctrl+C to stop")
    
    subprocess.run(["streamlit", "run", dashboard_path])


def run_tests():
    """Run the test suite."""
    import subprocess
    
    print("🧪 Running tests...")
    subprocess.run(["pytest", "tests/", "-v"])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="DevOps Transformation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  refresh     Run weekly data refresh
  setup       Initialize database
  dashboard   Launch Streamlit dashboard
  test        Run test suite

Examples:
  python main.py refresh
  python main.py dashboard
  ENABLE_DOCS_GENERATION=true python main.py refresh
        """
    )
    
    parser.add_argument(
        'command',
        choices=['refresh', 'setup', 'dashboard', 'test'],
        help='Command to run'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    
    # Load configuration
    config = Config()
    
    # Execute command
    if args.command == 'setup':
        setup_database(config)
    
    elif args.command == 'refresh':
        run_weekly_refresh(config)
    
    elif args.command == 'dashboard':
        launch_dashboard()
    
    elif args.command == 'test':
        run_tests()


if __name__ == "__main__":
    main()
