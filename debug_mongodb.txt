#!/usr/bin/env python3
"""
Debug script to check MongoDB data for duplicates
"""

from src.data.mongodb import MongoDatabase
from src.utils.config import Config
import pandas as pd

def main():
    config = Config()
    
    # Connect to MongoDB
    if config.mongodb_uri:
        db = MongoDatabase(
            connection_string=config.mongodb_uri,
            database_name=config.mongodb_database
        )
    else:
        db = MongoDatabase(
            host=config.mongodb_host,
            port=config.mongodb_port,
            username=config.mongodb_username,
            password=config.mongodb_password,
            auth_source=config.mongodb_auth_source,
            database_name=config.mongodb_database
        )
    
    print("=" * 80)
    print("CHECKING MONGODB METRICS COLLECTION")
    print("=" * 80)
    
    # Get all metrics directly from collection
    all_metrics = list(db.metrics.find({}).sort([("pod_id", 1), ("week_date", -1), ("created_at", -1)]))
    print(f"\nTotal records in metrics collection: {len(all_metrics)}")
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_metrics)
    
    if df.empty:
        print("No data found!")
        return
    
    print(f"\nColumns: {list(df.columns)}")
    
    # Check for duplicates by (pod_id, week_date)
    if 'pod_id' in df.columns and 'week_date' in df.columns:
        print("\n" + "=" * 80)
        print("CHECKING FOR DUPLICATES (pod_id, week_date)")
        print("=" * 80)
        
        duplicates = df.groupby(['pod_id', 'week_date']).size()
        dup_entries = duplicates[duplicates > 1]
        
        if dup_entries.empty:
            print("✅ No duplicates found!")
        else:
            print(f"❌ Found {len(dup_entries)} duplicate (pod_id, week_date) pairs:\n")
            for (pod, week), count in dup_entries.items():
                print(f"  {pod} on {week}: {count} records")
                
                # Show details of duplicates
                dup_records = df[(df['pod_id'] == pod) & (df['week_date'] == week)]
                print(f"    created_at values:")
                for idx, row in dup_records.iterrows():
                    print(f"      - {row.get('created_at', 'N/A')} (DPI: {row.get('dpi', 'N/A')})")
                print()
    
    # Check unique values
    print("\n" + "=" * 80)
    print("UNIQUE VALUES")
    print("=" * 80)
    if 'pod_id' in df.columns:
        print(f"Unique pod_ids: {df['pod_id'].nunique()}")
        print(f"Pod IDs: {sorted(df['pod_id'].unique())}")
    
    if 'week_date' in df.columns:
        print(f"\nUnique week_dates: {df['week_date'].nunique()}")
        print(f"Week dates: {sorted(df['week_date'].unique())}")
    
    # Show sample data
    print("\n" + "=" * 80)
    print("SAMPLE DATA (first 10 records)")
    print("=" * 80)
    sample_cols = ['pod_id', 'week_date', 'created_at', 'dpi']
    available_cols = [col for col in sample_cols if col in df.columns]
    print(df[available_cols].head(10).to_string())
    
    print("\n" + "=" * 80)
    print("TESTING get_all_history() METHOD")
    print("=" * 80)
    
    # Test the get_all_history method
    history_df = db.get_all_history()
    print(f"\nRecords returned by get_all_history(): {len(history_df)}")
    
    if not history_df.empty and 'pod_id' in history_df.columns and 'week_date' in history_df.columns:
        hist_dups = history_df.groupby(['pod_id', 'week_date']).size()
        hist_dup_entries = hist_dups[hist_dups > 1]
        
        if hist_dup_entries.empty:
            print("✅ No duplicates in get_all_history() results!")
        else:
            print(f"❌ Found {len(hist_dup_entries)} duplicates in get_all_history() results:")
            for (pod, week), count in hist_dup_entries.items():
                print(f"  {pod} on {week}: {count} records")

if __name__ == "__main__":
    main()
