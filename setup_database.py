"""
Interactive setup script for initializing the database
Helps with first-time setup and data population
"""

import sys
from datetime import datetime
from database import MetricsDatabase
from data_fetcher import DataFetcher
import config


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def get_bearer_token():
    """Get bearer token from user"""
    print("Enter your Bearer Token for API authentication:")
    print("(This will be used to fetch data from TeamBook and DataSight)")
    token = input("Bearer Token: ").strip()
    
    if not token:
        print("❌ Bearer token is required!")
        sys.exit(1)
    
    return token


def initialize_database():
    """Initialize the database"""
    print_header("Database Initialization")
    
    print("Creating database schema...")
    db = MetricsDatabase(config.DB_PATH)
    print("✅ Database initialized successfully!")
    
    return db


def fetch_initial_data(bearer_token):
    """Fetch initial data from APIs"""
    print_header("Data Fetching")
    
    print("Do you want to fetch data now? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice != 'y':
        print("⏭️  Skipping data fetch. You can fetch data later from the dashboard.")
        return
    
    print("\nInitializing data fetcher...")
    fetcher = DataFetcher(bearer_token, config.DB_PATH)
    
    print("\n📊 Fetching current week data...")
    try:
        fetcher.refresh_current_week()
        print("✅ Current week data fetched successfully!")
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        print("You can try again later from the dashboard.")
        return
    
    print("\nDo you want to backfill historical data? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("How many months of historical data? (1-12): ", end="")
        try:
            months = int(input().strip())
            months = max(1, min(12, months))
            
            print(f"\n📈 Backfilling {months} months of historical data...")
            print("This may take a few minutes...")
            
            fetcher.backfill_historical_data(months=months)
            print("✅ Historical data backfilled successfully!")
            
        except ValueError:
            print("❌ Invalid input. Skipping backfill.")
        except Exception as e:
            print(f"❌ Error backfilling data: {e}")


def verify_data(db):
    """Verify data was loaded correctly"""
    print_header("Data Verification")
    
    pods = db.get_all_pods()
    print(f"📦 Total pods in database: {len(pods)}")
    
    if len(pods) > 0:
        print("\nSample pods:")
        for _, pod in pods.head(5).iterrows():
            print(f"  - {pod['pod_name']} (ID: {pod['pod_id']})")
    
    latest = db.get_latest_metrics()
    print(f"\n📊 Latest metrics records: {len(latest)}")
    
    if len(latest) > 0:
        print(f"\nTop 3 teams by DPI:")
        top_teams = latest.nlargest(3, 'DPI')
        for _, team in top_teams.iterrows():
            print(f"  🏆 {team['Team']}: DPI = {team['DPI']} ({team['Tier']})")


def main():
    """Main setup workflow"""
    print_header("DevOps Gamification Dashboard - Database Setup")
    
    print("This script will help you set up the database and fetch initial data.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    # Step 1: Initialize database
    db = initialize_database()
    
    # Step 2: Get bearer token
    print_header("API Configuration")
    bearer_token = get_bearer_token()
    
    # Step 3: Fetch data
    fetch_initial_data(bearer_token)
    
    # Step 4: Verify
    verify_data(db)
    
    # Final message
    print_header("Setup Complete!")
    print("✅ Database is ready to use!")
    print("\nNext steps:")
    print("  1. Run the dashboard: streamlit run app.py")
    print("  2. Enter your bearer token in the sidebar")
    print("  3. Click 'Refresh Data' to update metrics")
    print("\n💡 Tip: Set up a weekly cron job to automatically refresh data")
    print("   See README_API_INTEGRATION.md for details")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)
