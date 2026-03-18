"""
Quick database population script
Fetches data from YAML registry and populates the database
"""

from data_fetcher import DataFetcher
import config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize with DataSight token only (uses YAML registry)
fetcher = DataFetcher(
    datasight_token=config.DATASIGHT_BEARER_TOKEN,
    db_path=config.DB_PATH
)

# Fetch current week data from YAML apps
fetcher.refresh_current_week()

print("✅ Database populated!")
