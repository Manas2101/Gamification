"""
Weekly data refresh script
Run this script via cron/scheduler to automatically fetch weekly data
No UI interaction required - uses .env file for credentials
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import DataFetcher
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weekly_refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main refresh function"""
    logger.info("=" * 60)
    logger.info("Starting weekly data refresh")
    logger.info("=" * 60)
    
    # Check if bearer tokens are configured
    if not config.TEAMBOOK_BEARER_TOKEN:
        logger.error("❌ TEAMBOOK_BEARER_TOKEN not found in environment!")
        logger.error("Please create a .env file with your bearer tokens")
        logger.error("See .env.example for template")
        sys.exit(1)
    
    if not config.DATASIGHT_BEARER_TOKEN:
        logger.error("❌ DATASIGHT_BEARER_TOKEN not found in environment!")
        logger.error("Please create a .env file with your bearer tokens")
        logger.error("See .env.example for template")
        sys.exit(1)
    
    try:
        # Initialize fetcher with separate tokens
        logger.info("Initializing data fetcher...")
        logger.info(f"Using separate tokens for TeamBook and DataSight APIs")
        fetcher = DataFetcher(
            config.TEAMBOOK_BEARER_TOKEN, 
            config.DATASIGHT_BEARER_TOKEN,
            config.DB_PATH
        )
        
        # Fetch current week data
        logger.info("Fetching current week data...")
        fetcher.refresh_current_week()
        
        # Cleanup old data - keep only last 5 weeks
        logger.info(f"Cleaning up old data (keeping last {config.MAX_WEEKS_TO_KEEP} weeks)...")
        fetcher.cleanup_old_data(max_weeks=config.MAX_WEEKS_TO_KEEP)
        
        # Get summary
        latest = fetcher.get_latest_dashboard_data()
        logger.info(f"✅ Successfully fetched data for {len(latest)} pods")
        
        if len(latest) > 0:
            avg_dpi = latest['DPI'].mean()
            logger.info(f"📊 Average DPI: {avg_dpi:.1f}")
            logger.info(f"🏆 Top team: {latest.iloc[0]['Team']} (DPI: {latest.iloc[0]['DPI']})")
        
        logger.info("=" * 60)
        logger.info("Weekly refresh completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error during refresh: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
