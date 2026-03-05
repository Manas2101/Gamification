"""
Automated database setup script for deployment
Initializes database and optionally fetches initial data
No interactive prompts - uses environment variables from .env
"""

import sys
import logging
from datetime import datetime
from database import MetricsDatabase
from data_fetcher import DataFetcher
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize the database"""
    logger.info("=" * 60)
    logger.info("Database Initialization")
    logger.info("=" * 60)
    
    logger.info("Creating database schema...")
    db = MetricsDatabase(config.DB_PATH)
    logger.info("✅ Database initialized successfully!")
    
    return db


def fetch_initial_data(fetch_data=True, backfill_months=0):
    """
    Fetch initial data from APIs
    
    Args:
        fetch_data: Whether to fetch current week data (default: True)
        backfill_months: Number of months to backfill (default: 0)
    """
    if not fetch_data:
        logger.info("Skipping data fetch (fetch_data=False)")
        return
    
    # Check if tokens are configured
    logger.info("Checking bearer tokens...")
    logger.info(f"TEAMBOOK_BEARER_TOKEN configured: {bool(config.TEAMBOOK_BEARER_TOKEN)}")
    logger.info(f"DATASIGHT_BEARER_TOKEN configured: {bool(config.DATASIGHT_BEARER_TOKEN)}")
    
    if config.TEAMBOOK_BEARER_TOKEN:
        logger.info(f"TeamBook token length: {len(config.TEAMBOOK_BEARER_TOKEN)}")
    if config.DATASIGHT_BEARER_TOKEN:
        logger.info(f"DataSight token length: {len(config.DATASIGHT_BEARER_TOKEN)}")
    
    if not config.TEAMBOOK_BEARER_TOKEN or not config.DATASIGHT_BEARER_TOKEN:
        logger.warning("⚠️ Bearer tokens not configured in .env file")
        logger.warning("Skipping data fetch. Configure tokens and run weekly_refresh.py")
        return
    
    logger.info("=" * 60)
    logger.info("Data Fetching")
    logger.info("=" * 60)
    
    logger.info("Initializing data fetcher...")
    fetcher = DataFetcher(
        config.TEAMBOOK_BEARER_TOKEN,
        config.DATASIGHT_BEARER_TOKEN,
        config.DB_PATH
    )
    
    logger.info("📊 Fetching current week data...")
    try:
        fetcher.refresh_current_week()
        logger.info("✅ Current week data fetched successfully!")
    except Exception as e:
        logger.error(f"❌ Error fetching data: {e}")
        logger.info("You can fetch data later using weekly_refresh.py")
        return
    
    # Backfill historical data if requested
    if backfill_months > 0:
        logger.info(f"📈 Backfilling {backfill_months} months of historical data...")
        try:
            fetcher.backfill_historical_data(months=backfill_months)
            logger.info("✅ Historical data backfilled successfully!")
        except Exception as e:
            logger.error(f"❌ Error backfilling data: {e}")
    
    # Cleanup old data
    logger.info(f"🧹 Cleaning up old data (keeping last {config.MAX_WEEKS_TO_KEEP} weeks)...")
    fetcher.cleanup_old_data(max_weeks=config.MAX_WEEKS_TO_KEEP)


def verify_data(db):
    """Verify data was loaded correctly"""
    logger.info("=" * 60)
    logger.info("Data Verification")
    logger.info("=" * 60)
    
    pods = db.get_all_pods()
    logger.info(f"📦 Total pods in database: {len(pods)}")
    
    if len(pods) > 0:
        logger.info("\nSample pods:")
        for _, pod in pods.head(5).iterrows():
            logger.info(f"  - {pod['pod_name']} (ID: {pod['pod_id']})")
    
    latest = db.get_latest_metrics()
    logger.info(f"\n📊 Latest metrics records: {len(latest)}")
    
    if len(latest) > 0:
        logger.info(f"\nTop 3 teams by DPI:")
        top_teams = latest.nlargest(3, 'DPI')
        for _, team in top_teams.iterrows():
            logger.info(f"  🏆 {team['Team']}: DPI = {team['DPI']} ({team['Tier']})")


def main():
    """
    Main setup workflow - fully automated
    
    Environment variables (from .env):
        TEAMBOOK_BEARER_TOKEN - TeamBook API token
        DATASIGHT_BEARER_TOKEN - DataSight API token
        DB_PATH - Database file path (default: metrics.db)
        MAX_WEEKS_TO_KEEP - Data retention period (default: 5)
    """
    logger.info("=" * 60)
    logger.info("DevOps Gamification Dashboard - Database Setup")
    logger.info("=" * 60)
    
    # Step 1: Initialize database
    db = initialize_database()
    
    # Step 2: Fetch data (if tokens configured)
    fetch_initial_data(fetch_data=True, backfill_months=0)
    
    # Step 3: Verify
    verify_data(db)
    
    # Final message
    logger.info("=" * 60)
    logger.info("Setup Complete!")
    logger.info("=" * 60)
    logger.info("✅ Database is ready to use!")
    logger.info("\nNext steps:")
    logger.info("  1. Configure tokens in .env file (if not done)")
    logger.info("  2. Run: streamlit run app.py")
    logger.info("  3. Set up weekly cron: python weekly_refresh.py")
    logger.info("\n💡 See SECURE_SETUP.md for deployment details")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}", exc_info=True)
        sys.exit(1)
