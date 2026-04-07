"""
MongoDB Database Module
=======================

MongoDB database operations for storing and retrieving pod metrics.

Provides persistent storage with historical tracking for:
    - Pod information and metadata
    - Weekly metrics snapshots
    - Historical trends and comparisons

Example:
    >>> from src.data.mongodb import MongoDatabase
    >>> db = MongoDatabase("mongodb://localhost:27017", "devops_metrics")
    >>> db.upsert_pod(pod_id="123", pod_name="MyPod", ...)

Author: DevOps Transformation Team
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, OperationFailure
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None

# Configure module logger
logger = logging.getLogger(__name__)


class MongoDatabase:
    """
    MongoDB database handler for metrics storage.
    
    Manages all database operations including collection creation,
    data insertion, updates, and queries.
    
    Attributes:
        connection_string (str): MongoDB connection string
        database_name (str): Name of the database
        
    Example:
        >>> db = MongoDatabase("mongodb://localhost:27017", "devops_metrics")
        >>> db.upsert_pod("123", "MyPod", "Java", "BU1", "Tier 1")
        >>> df = db.get_latest_metrics()
    """
    
    def __init__(self, connection_string: str = None, database_name: str = "devops_metrics"):
        """
        Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB connection URI
            database_name: Name of the database to use
            
        Raises:
            ImportError: If pymongo is not installed
            ConnectionFailure: If cannot connect to MongoDB
        """
        if not PYMONGO_AVAILABLE:
            raise ImportError(
                "pymongo is not installed. Install it with: pip install pymongo"
            )
        
        if not connection_string:
            connection_string = "mongodb://localhost:27017"
        
        self.connection_string = connection_string
        self.database_name = database_name
        
        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            logger.info(f"Connected to MongoDB: {database_name}")
            
            # Initialize collections
            self._init_collections()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _init_collections(self):
        """Initialize collections and indexes."""
        # Pods collection
        self.pods = self.db['pods']
        self.pods.create_index([("pod_id", ASCENDING)], unique=True)
        
        # Metrics collection
        self.metrics = self.db['metrics']
        self.metrics.create_index([("pod_id", ASCENDING), ("week_date", DESCENDING)])
        self.metrics.create_index([("created_at", DESCENDING)])
        
        logger.info("MongoDB collections initialized")
    
    def upsert_pod(
        self,
        pod_id: str,
        pod_name: str,
        stack: str = "",
        business_unit: str = "",
        tier: str = ""
    ):
        """
        Insert or update pod information.
        
        Args:
            pod_id: Unique pod identifier
            pod_name: Pod display name
            stack: Technology stack
            business_unit: Business unit name
            tier: Application tier
        """
        pod_data = {
            "pod_id": pod_id,
            "pod_name": pod_name,
            "stack": stack,
            "business_unit": business_unit,
            "tier": tier,
            "updated_at": datetime.utcnow()
        }
        
        self.pods.update_one(
            {"pod_id": pod_id},
            {"$set": pod_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True
        )
        logger.debug(f"Upserted pod: {pod_id}")
    
    def insert_weekly_metrics(self, metrics: Dict):
        """
        Insert weekly metrics snapshot.
        
        Args:
            metrics: Dictionary containing all metrics and scores
        """
        metrics_data = metrics.copy()
        metrics_data['created_at'] = datetime.utcnow()
        
        # Ensure week_date is present
        if 'week_date' not in metrics_data:
            metrics_data['week_date'] = datetime.utcnow().strftime('%Y-%m-%d')
        
        self.metrics.insert_one(metrics_data)
        logger.debug(f"Inserted metrics for pod: {metrics.get('pod_id')}")
    
    def get_latest_metrics(self) -> pd.DataFrame:
        """
        Get latest metrics for all pods.
        
        Returns:
            DataFrame with latest metrics for each pod
        """
        pipeline = [
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": "$pod_id",
                "latest": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$latest"}}
        ]
        
        results = list(self.metrics.aggregate(pipeline))
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Remove MongoDB _id field
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        return df
    
    def get_pod_history(self, pod_id: str, limit: int = 52) -> pd.DataFrame:
        """
        Get historical metrics for a specific pod.
        
        Args:
            pod_id: Pod identifier
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with historical metrics
        """
        results = list(
            self.metrics.find(
                {"pod_id": pod_id}
            ).sort("created_at", DESCENDING).limit(limit)
        )
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Remove MongoDB _id field
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        # Sort by date ascending for display
        if 'created_at' in df.columns:
            df = df.sort_values('created_at')
        
        return df
    
    def get_all_history(self, limit_per_pod: int = 52) -> pd.DataFrame:
        """
        Get historical metrics for all pods.
        
        Args:
            limit_per_pod: Maximum records per pod
            
        Returns:
            DataFrame with all historical metrics
        """
        pipeline = [
            {"$sort": {"pod_id": 1, "created_at": -1}},
            {"$group": {
                "_id": "$pod_id",
                "records": {"$push": "$$ROOT"}
            }},
            {"$project": {
                "records": {"$slice": ["$records", limit_per_pod]}
            }},
            {"$unwind": "$records"},
            {"$replaceRoot": {"newRoot": "$records"}}
        ]
        
        results = list(self.metrics.aggregate(pipeline))
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Remove MongoDB _id field
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        return df
    
    def get_leaderboard(self, metric: str = 'dpi', limit: int = 10) -> pd.DataFrame:
        """
        Get top performers by metric.
        
        Args:
            metric: Metric to rank by (default: dpi)
            limit: Number of top pods to return
            
        Returns:
            DataFrame with top performers
        """
        pipeline = [
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": "$pod_id",
                "latest": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$latest"}},
            {"$sort": {metric: -1}},
            {"$limit": limit}
        ]
        
        results = list(self.metrics.aggregate(pipeline))
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Remove MongoDB _id field
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        return df
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_pods': self.pods.count_documents({}),
            'total_metrics': self.metrics.count_documents({}),
            'database_name': self.database_name
        }
    
    def backup_to_json(self, output_dir: str = "backups"):
        """
        Backup database to JSON files.
        
        Args:
            output_dir: Directory to save backup files
        """
        import os
        import json
        from datetime import datetime
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup pods
        pods_data = list(self.pods.find({}))
        pods_file = os.path.join(output_dir, f'pods_{timestamp}.json')
        with open(pods_file, 'w') as f:
            json.dump(pods_data, f, default=str, indent=2)
        
        # Backup metrics
        metrics_data = list(self.metrics.find({}))
        metrics_file = os.path.join(output_dir, f'metrics_{timestamp}.json')
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, default=str, indent=2)
        
        logger.info(f"Backup completed: {output_dir}")
        return {'pods': pods_file, 'metrics': metrics_file}
    
    def close(self):
        """Close MongoDB connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("MongoDB connection closed")
