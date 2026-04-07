#!/usr/bin/env python3
"""
Test MongoDB Connection
=======================

Quick test script to verify MongoDB connection with your credentials.

Usage:
    python test_mongo_connection.py
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test MongoDB connection using environment variables."""
    print("=" * 60)
    print("Testing MongoDB Connection")
    print("=" * 60)
    print()
    
    # Load credentials from .env
    host = os.getenv("MONGO_HOST")
    port = os.getenv("MONGO_PORT")
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    auth_source = os.getenv("MONGO_AUTHSOURCE")
    db_name = os.getenv("MONGO_DB_NAME")
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'Not set'}")
    print(f"Auth Source: {auth_source}")
    print(f"Database: {db_name}")
    print()
    
    if not all([host, port, username, password, auth_source, db_name]):
        print("❌ Missing required environment variables!")
        print()
        print("Required in .env file:")
        print("  MONGO_HOST")
        print("  MONGO_PORT")
        print("  MONGO_USERNAME")
        print("  MONGO_PASSWORD")
        print("  MONGO_AUTHSOURCE")
        print("  MONGO_DB_NAME")
        return False
    
    try:
        from src.data.mongodb import MongoDatabase
        
        print("Connecting to MongoDB...")
        print()
        
        # Connect using individual parameters
        db = MongoDatabase(
            host=host,
            port=int(port),
            username=username,
            password=password,
            auth_source=auth_source,
            database_name=db_name
        )
        
        # Get statistics
        stats = db.get_statistics()
        
        print("✅ Connection successful!")
        print()
        print("Database Statistics:")
        print(f"  - Database: {stats['database_name']}")
        print(f"  - Total Pods: {stats['total_pods']}")
        print(f"  - Total Metrics: {stats['total_metrics']}")
        print()
        
        # Test insert
        print("Testing data insertion...")
        test_metrics = {
            'pod_id': 'test_pod_001',
            'week_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'dpi': 85.5,
            'Release_Velocity_Score': 90.0,
            'Git_Hygiene_Score': 85.0,
            'Pipeline_Maturity_Score': 80.0,
            'Compliance_Score': 85.0,
            'Quality_Security_Score': 90.0,
            'Adoption_Score': 75.0,
            'apis_published_iadp': True,
            'apis_published_apix': False,
            'ai_devops_onboarded': True
        }
        
        db.insert_weekly_metrics(test_metrics)
        print("✅ Test data inserted successfully!")
        print()
        
        # Close connection
        db.close()
        
        print("=" * 60)
        print("All tests passed! MongoDB is ready to use.")
        print("=" * 60)
        print()
        print("Next step: Run 'python main.py refresh'")
        print()
        
        return True
        
    except ImportError:
        print("❌ pymongo not installed!")
        print()
        print("Install it with:")
        print("  pip install pymongo")
        print()
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Please check:")
        print("  1. MongoDB host and port are correct")
        print("  2. Username and password are correct")
        print("  3. Auth source is correct")
        print("  4. Database name is correct")
        print("  5. Network connectivity to MongoDB server")
        print("  6. MongoDB server is running and accessible")
        print()
        import traceback
        print("Full error:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection()
