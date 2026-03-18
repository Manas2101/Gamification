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
    
    def __init__(self, datasight_token: str, db_path: str = "metrics.db", registry_dir: str = None):
        """
        Initialize data fetcher
        
        Args:
            datasight_token: Bearer token for DataSight API
            db_path: Path to SQLite database
            registry_dir: Path to YAML registry directory (optional)
        """
        self.collector = MetricsCollector(datasight_token, registry_dir)
        self.db = MetricsDatabase(db_path)
        self.calculator = MetricsCalculator()
    
    def fetch_and_store_weekly_data(self, week_date: Optional[datetime] = None):
        """
        Fetch metrics for all apps and store in database
        
        Args:
            week_date: Week date to fetch (defaults to current week Monday)
        """
        if week_date is None:
            week_date = datetime.now()
        
        # Normalize to Monday/week-start
        week_date = week_date - timedelta(days=week_date.weekday())
        week_date = week_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"Starting data fetch for week starting: {week_date.strftime('%Y-%m-%d')}")
        
        # Fetch raw metrics from APIs (includes YAML data + API metrics)
        raw_metrics = self.collector.collect_weekly_metrics(week_date)
        
        # Process each app's metrics
        for app_metrics in raw_metrics:
            try:
                # Generate random values for missing fields (if needed)
                random_fields = self.calculator.randomize_missing_fields()
                
                # Merge API data with random fields (API data takes precedence)
                complete_metrics = {
                    **random_fields,
                    **app_metrics,  # API + YAML data overwrites random
                    'week_date': week_date,
                    'week_start': week_date
                }
                
                # Calculate scores and DPI
                calculated_scores = self.calculator.calculate_all_scores(complete_metrics)
                
                # Merge all data
                final_metrics = {
                    **complete_metrics,
                    **calculated_scores
                }
                
                # Store pod information (using EIM as pod_id)
                self.db.upsert_pod(
                    pod_id=final_metrics['pod_id'],  # EIM ID
                    pod_name=final_metrics.get('app_name', final_metrics['pod_name']),
                    stack=final_metrics.get('stack'),
                    business_unit=final_metrics.get('business_unit'),
                    tier=final_metrics.get('tier')
                )
                
                # Store weekly metrics
                self.db.insert_weekly_metrics(final_metrics)
                
                logger.info(f"Stored metrics for app: {final_metrics.get('app_name')} (EIM: {final_metrics['eim']}, DPI: {final_metrics['dpi']})")
                
            except Exception as e:
                logger.error(f"Error processing app {app_metrics.get('app_name', app_metrics.get('pod_name'))}: {e}", exc_info=True)
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
        current_week = datetime.now().replace(day=1)
        logger.info("Refreshing current week data...")
        self.fetch_and_store_weekly_data(current_week)
    
    def backfill_historical_data(self, months: int = 3):
        """
        Backfill historical data for previous months
        
        Args:
            months: Number of months to backfill
        """
        logger.info(f"Starting backfill for {months} months")
        
        current_date = datetime.now().replace(day=1)
        
        for i in range(months):
            week_date = current_date - timedelta(days=30 * i)
            logger.info(f"Backfilling data for: {week_date.strftime('%Y-%m')}")
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


def main():
    """Example usage"""
    # Replace with actual bearer token
    DATASIGHT_TOKEN = "your_datasight_bearer_token_here"
    
    # Initialize fetcher (no TeamBook token needed - uses YAML registry)
    fetcher = DataFetcher(DATASIGHT_TOKEN)
    
    # Fetch current week data
    fetcher.refresh_current_week()
    
    # Cleanup old data (keep only 5 weeks)
    fetcher.cleanup_old_data(max_weeks=5)
    
    # Get latest data for dashboard
    latest_data = fetcher.get_latest_dashboard_data()
    print(f"Fetched {len(latest_data)} apps")
    print(latest_data.head())


if __name__ == "__main__":
    main()
