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
from src.core.calculator import MetricsCalculator
from src.core.badges import BadgeEngine

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


def run_weekly_refresh(config: Config):
    """
    Run weekly data refresh to collect metrics.
    
    Args:
        config: Application configuration.
    """
    logger.info("=" * 60)
    logger.info("Starting Weekly Data Refresh")
    logger.info("=" * 60)
    
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
    
    # Initialize GitHub client if token available
    github_client = None
    if config.github_token:
        github_client = GitHubClient(config.github_token)
        logger.info("GitHub hygiene checking enabled")
    else:
        logger.warning("No GitHub token - hygiene checks will be skipped")
    
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
            
            # Calculate Git hygiene if GitHub client available
            if github_client and app.repos:
                total_hygiene = 0
                total_critical = 0
                total_warnings = 0
                
                logger.info(f"  Checking hygiene for {len(app.repos)} repositories")
                for repo in app.repos:
                    try:
                        # Pass full_url for enterprise GitHub support
                        hygiene = github_client.calculate_hygiene_score(
                            repo.full_name, 
                            full_url=repo.full_url
                        )
                        total_hygiene += hygiene['score']
                        total_critical += hygiene['critical']
                        total_warnings += hygiene['warnings']
                        logger.info(f"    {repo.full_name}: score={hygiene['score']}")
                    except Exception as e:
                        logger.warning(f"  Hygiene check failed for {repo.full_name}: {e}")
                
                if app.repos:
                    metrics['git_hygiene_score'] = total_hygiene / len(app.repos)
                    metrics['git_hygiene_violations_critical'] = total_critical
                    metrics['git_hygiene_violations_warnings'] = total_warnings
            
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
            failed += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Weekly Refresh Complete")
    logger.info("=" * 60)
    logger.info(f"  Processed: {processed}")
    logger.info(f"  Failed: {failed}")
    
    # Get updated stats
    stats = db.get_statistics()
    logger.info(f"  Average DPI: {stats['average_dpi']}")
    
    print(f"\n✅ Weekly refresh complete!")
    print(f"   Processed: {processed} applications")
    print(f"   Failed: {failed}")
    print(f"   Average DPI: {stats['average_dpi']}")


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
