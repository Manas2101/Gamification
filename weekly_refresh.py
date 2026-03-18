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

        logger.info(f"Using separate tokens for TeamBook and DataSight APIs")

        fetcher = DataFetcher(

            config.TEAMBOOK_BEARER_TOKEN,

            config.DATASIGHT_BEARER_TOKEN,

            config.DB_PATH

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

datafetcher.py

"""

Main data fetcher orchestrator

Coordinates API calls, calculations, and database storage

"""

 

from datetime import datetime, timedelta

from typing import Optional

import logging

 

from api_integration import MetricsCollector

from database import MetricsDatabase

from metrics_calculator import MetricsCalculator

 

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

 

class DataFetcher:

    """Orchestrates the complete data fetching and storage workflow"""

   

    def __init__(self, teambook_token: str, datasight_token: str = None, db_path: str = "metrics.db"):

        """

        Initialize data fetcher

       

        Args:

            teambook_token: Bearer token for TeamBook API

            datasight_token: Bearer token for DataSight API (optional, defaults to teambook_token)

            db_path: Path to SQLite database

        """

        self.collector = MetricsCollector(teambook_token, datasight_token)

        self.db = MetricsDatabase(db_path)

        self.calculator = MetricsCalculator()

   

    def fetch_and_store_weekly_data(self, week_date: Optional[datetime] = None):

        """

        Fetch metrics for all pods and store in database

       

        Args:

            week_date: Week date to fetch (defaults to current month)

        """

        if week_date is None:

            week_date = datetime.now()

 

        # Normalize to Monday/week-start so DB, latest-week selection, and trends align.

        week_date = week_date - timedelta(days=week_date.weekday())

        week_date = week_date.replace(hour=0, minute=0, second=0, microsecond=0)

 

        logger.info(f"Starting data fetch for week starting: {week_date.strftime('%Y-%m-%d')}")

       

        # Fetch raw metrics from APIs

        raw_metrics = self.collector.collect_weekly_metrics(week_date)

       

        # Process each pod's metrics

        for pod_metrics in raw_metrics:

            try:

                # Generate random values for missing fields

                random_fields = self.calculator.randomize_missing_fields()

               

                # Merge API data with random fields

                complete_metrics = {

                    **pod_metrics,

                    **random_fields

                }

               

                # Calculate scores and DPI

                calculated_scores = self.calculator.calculate_all_scores(complete_metrics)

               

                # Merge all data

                final_metrics = {

                    **complete_metrics,

                    **calculated_scores,

                    'week_date': week_date,

                    'week_start': week_date

                }

               

                # Store pod information

                self.db.upsert_pod(

                    pod_id=final_metrics['pod_id'],

                    pod_name=final_metrics['pod_name'],

                    stack=final_metrics.get('stack'),

                    business_unit=final_metrics.get('business_unit'),

                    tier=final_metrics.get('tier')

                )

               

                # Store weekly metrics

                self.db.insert_weekly_metrics(final_metrics)

               

                logger.info(f"Stored metrics for pod: {final_metrics['pod_name']} (DPI: {final_metrics['dpi']})")

               

            except Exception as e:

                logger.error(f"Error processing pod {pod_metrics.get('pod_name')}: {e}")

                continue

       

        logger.info("Weekly data fetch completed successfully")

   

    def get_latest_dashboard_data(self):

        """

        Get latest metrics for dashboard display

       

        Returns:

            DataFrame with latest metrics

        """

        return self.db.get_latest_metrics()

   

    def get_trend_data(self, pod_id: Optional[int] = None, weeks: int = 12):

        """

        Get historical trend data

       

        Args:

            pod_id: Optional pod ID to filter

            weeks: Number of weeks to retrieve

           

        Returns:

            DataFrame with historical data

        """

        return self.db.get_historical_metrics(pod_id, weeks)

   

    def refresh_current_week(self):

        """Refresh data for the current week"""

        current_week = datetime.now()

        logger.info("Refreshing current week data...")

        self.fetch_and_store_weekly_data(current_week)

   

    def backfill_historical_data(self, months: int = 3):

        """

        Backfill historical data for previous months

       

        Args:

            months: Number of months to backfill

        """

        logger.info(f"Starting backfill for {months} months")

       

        current_date = datetime.now()

       

        for i in range(months):

            week_date = current_date - timedelta(weeks=i)

            logger.info(f"Backfilling data for week starting: {week_date.strftime('%Y-%m-%d')}")

            self.fetch_and_store_weekly_data(week_date)

       

        logger.info("Backfill completed")

   

    def cleanup_old_data(self, max_weeks: int = 5):

        """

        Remove data older than specified number of weeks

        Keeps only the most recent N weeks of data

       

        Args:

            max_weeks: Maximum number of weeks to retain (default: 5)

        """

        logger.info(f"Cleaning up data older than {max_weeks} weeks")

       

        try:

            import sqlite3

            conn = sqlite3.connect(self.db.db_path)

            cursor = conn.cursor()

           

            # Get all unique week dates, sorted descending

            cursor.execute('''

                SELECT DISTINCT week_date

                FROM weekly_metrics

                ORDER BY week_date DESC

            ''')

           

            all_weeks = [row[0] for row in cursor.fetchall()]

           

            if len(all_weeks) > max_weeks:

                # Keep only the most recent N weeks

                weeks_to_keep = all_weeks[:max_weeks]

                weeks_to_delete = all_weeks[max_weeks:]

               

                logger.info(f"Found {len(all_weeks)} weeks, keeping {len(weeks_to_keep)}, deleting {len(weeks_to_delete)}")

               

                # Delete old weeks

                for week in weeks_to_delete:

                    cursor.execute('DELETE FROM weekly_metrics WHERE week_date = ?', (week,))

                    logger.info(f"Deleted data for week: {week}")

               

                conn.commit()

                logger.info(f"✅ Cleanup completed. Retained {max_weeks} most recent weeks")

            else:

                logger.info(f"Only {len(all_weeks)} weeks found. No cleanup needed.")

           

            conn.close()

           

        except Exception as e:

            logger.error(f"Error during cleanup: {e}")

 

    def normalize_existing_week_dates(self):

        """Normalize existing week_date/week_start DB values to YYYY-MM-DD.

 

        Useful once after older refreshes stored timestamped values like

        2026-03-01 11:10:41.448510 instead of clean week buckets.

        """

        logger.info("Normalizing existing week_date/week_start values...")

        try:

            import sqlite3

            conn = sqlite3.connect(self.db.db_path)

            cursor = conn.cursor()

            cursor.execute(

                """

                UPDATE weekly_metrics

                SET

                    week_date = date(week_date),

                    week_start = date(week_start)

                WHERE week_date IS NOT NULL OR week_start IS NOT NULL

                """

            )

            conn.commit()

            conn.close()

            logger.info("✅ Existing week dates normalized")

        except Exception as e:

            logger.error(f"Error normalizing week dates: {e}")

 

def main():

    """Example usage"""

    # Replace with actual bearer tokens

    TEAMBOOK_TOKEN = "your_teambook_bearer_token_here"

    DATASIGHT_TOKEN = "your_datasight_bearer_token_here"

   

    # Initialize fetcher with separate tokens

    fetcher = DataFetcher(TEAMBOOK_TOKEN, DATASIGHT_TOKEN)

   

    # Fetch current week data

    fetcher.refresh_current_week()

   

    # Cleanup old data (keep only 5 weeks)

    fetcher.cleanup_old_data(max_weeks=5)

   

    # Get latest data for dashboard

    latest_data = fetcher.get_latest_dashboard_data()

    print(f"Fetched {len(latest_data)} pods")

    print(latest_data.head())

 

if __name__ == "__main__":

    main()

