#!/usr/bin/env python3
"""
MongoDB Setup Helper
====================

Quick setup for MongoDB integration with Gamification platform.

Usage:
    python setup_mongodb.py              # Interactive setup
    python setup_mongodb.py test         # Test existing connection
    
After setup, run: python main.py refresh

Your credentials:
    Host: (your MongoDB host)
    Port: (your MongoDB port)
    Username: (your username)
    Password: devops_tooling_#123
    Database: devops_tooling
"""

import os
import sys

def create_env_file():
    """Create .env file with MongoDB configuration."""
    print("=" * 60)
    print("MongoDB Configuration Setup")
    print("=" * 60)
    print()
    
    # Get credentials from user
    print("Please enter your MongoDB credentials:")
    print()
    
    host = input("MongoDB Host (e.g., mongodb.example.com): ").strip()
    port = input("MongoDB Port [27017]: ").strip() or "27017"
    username = input("MongoDB Username: ").strip()
    password = input("MongoDB Password: ").strip()
    database = input("MongoDB Database Name [devops_tooling]: ").strip() or "devops_tooling"
    
    print()
    print("Choose connection type:")
    print("1. Standard MongoDB (mongodb://)")
    print("2. MongoDB Atlas (mongodb+srv://)")
    choice = input("Enter choice [1]: ").strip() or "1"
    
    # Construct MongoDB URI
    if choice == "2":
        # MongoDB Atlas
        mongodb_uri = f"mongodb+srv://{username}:{password}@{host}/?retryWrites=true&w=majority"
    else:
        # Standard MongoDB
        mongodb_uri = f"mongodb://{username}:{password}@{host}:{port}"
    
    # Check if .env already exists
    env_path = ".env"
    if os.path.exists(env_path):
        print()
        print(f"⚠️  {env_path} already exists!")
        overwrite = input("Do you want to append MongoDB config? [y/N]: ").strip().lower()
        if overwrite != 'y':
            print("Aborted.")
            return
        mode = 'a'
        print()
    else:
        mode = 'w'
    
    # Write to .env file
    with open(env_path, mode) as f:
        if mode == 'a':
            f.write("\n\n")
        f.write("# MongoDB Configuration\n")
        f.write(f"MONGODB_URI={mongodb_uri}\n")
        f.write(f"MONGODB_DATABASE={database}\n")
    
    print()
    print("✅ MongoDB configuration saved to .env")
    print()
    
    # Test connection
    test = input("Do you want to test the connection now? [Y/n]: ").strip().lower()
    if test != 'n':
        test_connection(mongodb_uri, database)

def test_connection(uri=None, database=None):
    """Test MongoDB connection."""
    print()
    print("=" * 60)
    print("Testing MongoDB Connection")
    print("=" * 60)
    print()
    
    # Load from .env if not provided
    if uri is None:
        from dotenv import load_dotenv
        load_dotenv()
        uri = os.getenv("MONGODB_URI")
        database = os.getenv("MONGODB_DATABASE", "devops_tooling")
    
    if not uri:
        print("❌ MONGODB_URI not found in .env file")
        return False
    
    try:
        from src.data.mongodb import MongoDatabase
        
        print(f"Connecting to: {uri.split('@')[1] if '@' in uri else uri}")
        print(f"Database: {database}")
        print()
        
        # Try to connect
        db = MongoDatabase(uri, database)
        
        # Get statistics
        stats = db.get_statistics()
        
        print("✅ Connection successful!")
        print()
        print("Database Statistics:")
        print(f"  - Database: {stats['database_name']}")
        print(f"  - Total Pods: {stats['total_pods']}")
        print(f"  - Total Metrics: {stats['total_metrics']}")
        print()
        
        db.close()
        return True
        
    except ImportError as e:
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
        print("  3. Database name is correct")
        print("  4. Network connectivity to MongoDB server")
        print("  5. MongoDB server is running")
        print()
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Just test connection
        test_connection()
    else:
        # Full setup
        create_env_file()

if __name__ == "__main__":
    main()
