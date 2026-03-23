"""
Weekly data refresh script

Run this script via cron/scheduler to automatically fetch weekly data

No UI interaction required - uses .env file for credentials

"""

 

import sys

import logging

from datetime import datetime, timedelta

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

        logger.info(f"Using DataSight API token")

        # Get GitHub token from environment (optional - for hygiene checking)
        github_token = os.getenv('GITHUB_TOKEN', '')

        fetcher = DataFetcher(

            datasight_token=config.DATASIGHT_BEARER_TOKEN,

            db_path=config.DB_PATH,

            registry_dir=None,

            github_token=github_token if github_token else None

        )

 

        # Normalize any older timestamped week buckets before writing new data.

        logger.info("Normalizing existing week_date/week_start values in DB...")

        fetcher.normalize_existing_week_dates()

 

        target_week = datetime.now() - timedelta(days=datetime.now().weekday())

        target_week = target_week.replace(hour=0, minute=0, second=0, microsecond=0)

        logger.info(f"Target week for this refresh: {target_week.strftime('%Y-%m-%d')}")

       

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
