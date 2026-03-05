"""
Example usage of the API integration
Demonstrates how to fetch and display data
Uses tokens from .env file - no prompts
"""

from datetime import datetime
from data_fetcher import DataFetcher
from database import MetricsDatabase
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_fetch_data():
    """Example: Fetch data from APIs using tokens from .env"""
    logger.info("=" * 60)
    logger.info("Example 1: Fetching Data from APIs")
    logger.info("=" * 60)
    
    # Check if tokens are configured
    if not config.TEAMBOOK_BEARER_TOKEN or not config.DATASIGHT_BEARER_TOKEN:
        logger.error("❌ Bearer tokens not configured in .env file")
        return
    
    # Initialize fetcher with separate tokens
    fetcher = DataFetcher(
        config.TEAMBOOK_BEARER_TOKEN,
        config.DATASIGHT_BEARER_TOKEN,
        config.DB_PATH
    )
    
    # Fetch current week data
    logger.info("\n📊 Fetching current week data...")
    fetcher.refresh_current_week()
    logger.info("✅ Data fetched successfully!")


def example_query_database():
    """Example: Query data from database"""
    print("\n" + "=" * 60)
    print("Example 2: Querying Database")
    print("=" * 60)
    
    db = MetricsDatabase(config.DB_PATH)
    
    # Get all pods
    print("\n📦 All Pods:")
    pods = db.get_all_pods()
    print(f"Total pods: {len(pods)}")
    if len(pods) > 0:
        print(pods[['pod_id', 'pod_name', 'tier']].head())
    
    # Get latest metrics
    print("\n📊 Latest Metrics:")
    latest = db.get_latest_metrics()
    print(f"Total records: {len(latest)}")
    if len(latest) > 0:
        print(latest[['Team', 'DPI', 'Tier', 'RF', 'LTDD']].head())
    
    # Get historical data
    print("\n📈 Historical Metrics (last 4 weeks):")
    history = db.get_historical_metrics(weeks=4)
    print(f"Total records: {len(history)}")
    if len(history) > 0:
        print(history[['Team', 'Week', 'DPI']].head(10))


def example_calculate_scores():
    """Example: Calculate scores manually"""
    print("\n" + "=" * 60)
    print("Example 3: Calculating Scores")
    print("=" * 60)
    
    from metrics_calculator import MetricsCalculator
    
    # Sample metrics
    sample_metrics = {
        'rf': 250,
        'lttd': 5.5,
        'ltdd_measurable': 0.95,
        'cfr': 0.12,
        'mttr': 1.5,
        'priv_access': 1,
        'ci': True,
        'cd': True,
        'iac': True,
        'rollback': True,
        'self_service': False,
        'cfr_reported': True,
        'automation_audited': True,
        'critical_data_present': True
    }
    
    print("\n📊 Input Metrics:")
    print(f"  RF: {sample_metrics['rf']}")
    print(f"  LTTD: {sample_metrics['lttd']} days")
    print(f"  CFR: {sample_metrics['cfr']}")
    print(f"  MTTR: {sample_metrics['mttr']} hours")
    
    # Calculate scores
    calculator = MetricsCalculator()
    scores = calculator.calculate_all_scores(sample_metrics)
    
    print("\n🎯 Calculated Scores:")
    print(f"  RF Score: {scores['rf_score']}")
    print(f"  Flow Score: {scores['flow_score']}")
    print(f"  CFR Score: {scores['cfr_score']}")
    print(f"  MTTR Score: {scores['mttr_score']}")
    print(f"  Priv Score: {scores['priv_score']}")
    print(f"  Automation Score: {scores['automation_score']}")
    print(f"  Stability Score: {scores['stability_score']}")
    print(f"\n🏆 Total DPI: {scores['dpi']}")
    print(f"📊 Tier: {scores['tier']}")


def example_api_calls():
    """Example: Direct API calls using tokens from .env"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Direct API Calls")
    logger.info("=" * 60)
    
    from api_integration import TeamBookAPI, DataSightAPI
    from datetime import datetime
    
    # Check if tokens are configured
    if not config.TEAMBOOK_BEARER_TOKEN or not config.DATASIGHT_BEARER_TOKEN:
        logger.error("❌ Bearer tokens not configured in .env file")
        return
    
    # TeamBook API
    logger.info("\n📦 Fetching pods from TeamBook...")
    teambook = TeamBookAPI(config.TEAMBOOK_BEARER_TOKEN)
    try:
        pods = teambook.get_pods()
        logger.info(f"✅ Found {len(pods)} pods")
        if len(pods) > 0:
            logger.info(f"Sample: {pods[0]}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    
    # DataSight API
    logger.info("\n📊 Fetching metrics from DataSight...")
    datasight = DataSightAPI(config.DATASIGHT_BEARER_TOKEN)
    
    # Example: Get metrics for pod ID 1251
    pod_id = 1251
    week_date = datetime(2025, 9, 1)
    
    try:
        metrics = datasight.get_all_metrics(pod_id, week_date, week_date)
        logger.info(f"✅ Metrics for pod {pod_id}:")
        logger.info(f"  MTTR: {metrics.get('mttr')}")
        logger.info(f"  LTTD: {metrics.get('lttd')}")
        logger.info(f"  RF: {metrics.get('rf')}")
        logger.info(f"  CFR: {metrics.get('cfr')}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")


def main():
    """Run all examples - uses tokens from .env file"""
    logger.info("\n" + "=" * 60)
    logger.info("DevOps Gamification - API Integration Examples")
    logger.info("=" * 60)
    
    logger.info("\nNote: Configure tokens in .env file before running")
    logger.info("      See .env.example for template\n")
    
    # Uncomment the examples you want to run:
    
    # example_fetch_data()  # Requires valid bearer token
    example_query_database()  # Works if database exists
    example_calculate_scores()  # Always works
    # example_api_calls()  # Requires valid bearer token
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
