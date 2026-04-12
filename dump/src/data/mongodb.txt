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
    
    def __init__(
        self, 
        connection_string: str = None, 
        database_name: str = "devops_metrics",
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None,
        auth_source: str = None
    ):
        """
        Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB connection URI (if provided, other params ignored)
            database_name: Name of the database to use
            host: MongoDB host (alternative to connection_string)
            port: MongoDB port (alternative to connection_string)
            username: MongoDB username (alternative to connection_string)
            password: MongoDB password (alternative to connection_string)
            auth_source: Authentication database (alternative to connection_string)
            
        Raises:
            ImportError: If pymongo is not installed
            ConnectionFailure: If cannot connect to MongoDB
        """
        if not PYMONGO_AVAILABLE:
            raise ImportError(
                "pymongo is not installed. Install it with: pip install pymongo"
            )
        
        self.database_name = database_name
        
        try:
            # Use connection string if provided
            if connection_string:
                self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
                self.connection_string = connection_string
            # Otherwise use individual parameters
            else:
                host = host or "localhost"
                port = port or 27017
                
                if username and password:
                    auth_source = auth_source or "admin"
                    self.client = MongoClient(
                        host=host,
                        port=port,
                        username=username,
                        password=password,
                        authSource=auth_source,
                        serverSelectionTimeoutMS=5000
                    )
                    self.connection_string = f"mongodb://{username}:***@{host}:{port}/?authSource={auth_source}"
                else:
                    self.client = MongoClient(host=host, port=port, serverSelectionTimeoutMS=5000)
                    self.connection_string = f"mongodb://{host}:{port}"
            
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
        Get latest metrics for all pods with pod metadata joined.
        
        Returns:
            DataFrame with latest metrics for each pod including tier, stack, business_unit
        """
        try:
            # First try the aggregation pipeline with join
            pipeline = [
                # Get latest metrics for each pod - sort by week_date first, then created_at
                {"$sort": {"week_date": -1, "created_at": -1}},
                {"$group": {
                    "_id": "$pod_id",
                    "latest": {"$first": "$$ROOT"}
                }},
                {"$replaceRoot": {"newRoot": "$latest"}},
                
                # Join with pods collection to get tier, stack, business_unit
                {"$lookup": {
                    "from": "pods",
                    "localField": "pod_id",
                    "foreignField": "pod_id",
                    "as": "pod_info"
                }},
                
                # Merge pod info into main document
                {"$addFields": {
                    "tier": {"$arrayElemAt": ["$pod_info.tier", 0]},
                    "stack": {"$arrayElemAt": ["$pod_info.stack", 0]},
                    "business_unit": {"$arrayElemAt": ["$pod_info.business_unit", 0]},
                    "pod_name": {"$arrayElemAt": ["$pod_info.pod_name", 0]}
                }},
                
                # Remove the pod_info array
                {"$unset": "pod_info"}
            ]
            
            results = list(self.metrics.aggregate(pipeline))
            
            if not results:
                logger.warning("No results from aggregation pipeline")
                return pd.DataFrame()
            
            df = pd.DataFrame(results)
            
            # Check if join worked by seeing if we have tier data
            if 'tier' not in df.columns or df['tier'].isna().all():
                logger.warning("MongoDB join didn't work, falling back to separate queries")
                return self._get_latest_metrics_fallback()
            
            # Remove MongoDB _id field
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            logger.info(f"Successfully joined {len(df)} records with pod metadata")
            
            # Debug: Log the dates we're returning
            if 'week_date' in df.columns:
                unique_dates = df['week_date'].unique()
                logger.info(f"Returning latest metrics with week_dates: {sorted(unique_dates)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error in get_latest_metrics aggregation: {e}")
            return self._get_latest_metrics_fallback()
    
    def _get_latest_metrics_fallback(self) -> pd.DataFrame:
        """
        Fallback method to get metrics and pod info separately then merge.
        """
        try:
            # Get latest metrics without join
            pipeline = [
                {"$sort": {"week_date": -1, "created_at": -1}},
                {"$group": {
                    "_id": "$pod_id",
                    "latest": {"$first": "$$ROOT"}
                }},
                {"$replaceRoot": {"newRoot": "$latest"}}
            ]
            
            metrics_results = list(self.metrics.aggregate(pipeline))
            if not metrics_results:
                return pd.DataFrame()
            
            metrics_df = pd.DataFrame(metrics_results)
            
            # Get all pod info
            pods_results = list(self.pods.find({}))
            if not pods_results:
                logger.warning("No pods found in pods collection")
                return metrics_df
            
            pods_df = pd.DataFrame(pods_results)
            
            # Merge on pod_id
            merged_df = metrics_df.merge(
                pods_df[['pod_id', 'pod_name', 'tier', 'stack', 'business_unit']], 
                on='pod_id', 
                how='left'
            )
            
            # Remove MongoDB _id fields
            for col in ['_id_x', '_id_y', '_id']:
                if col in merged_df.columns:
                    merged_df = merged_df.drop(col, axis=1)
            
            logger.info(f"Fallback merge successful: {len(merged_df)} records")
            return merged_df
            
        except Exception as e:
            logger.error(f"Error in fallback method: {e}")
            return pd.DataFrame()
    
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
        Get historical metrics for all pods with pod metadata joined.
        
        Args:
            limit_per_pod: Maximum records per pod
            
        Returns:
            DataFrame with all historical metrics including tier, stack, business_unit
        """
        try:
            # First try the aggregation pipeline with join
            # Group by pod_id AND week_date to get unique records per week
            pipeline = [
                {"$sort": {"pod_id": 1, "week_date": -1, "created_at": -1}},
                # First group by pod_id and week_date to get latest record for each week
                {"$group": {
                    "_id": {"pod_id": "$pod_id", "week_date": "$week_date"},
                    "latest": {"$first": "$$ROOT"}
                }},
                {"$replaceRoot": {"newRoot": "$latest"}},
                # Then group by pod_id to limit records per pod
                {"$sort": {"pod_id": 1, "week_date": -1}},
                {"$group": {
                    "_id": "$pod_id",
                    "records": {"$push": "$$ROOT"}
                }},
                {"$project": {
                    "records": {"$slice": ["$records", limit_per_pod]}
                }},
                {"$unwind": "$records"},
                {"$replaceRoot": {"newRoot": "$records"}},
                
                # Join with pods collection to get tier, stack, business_unit
                {"$lookup": {
                    "from": "pods",
                    "localField": "pod_id",
                    "foreignField": "pod_id",
                    "as": "pod_info"
                }},
                
                # Merge pod info into main document
                {"$addFields": {
                    "tier": {"$arrayElemAt": ["$pod_info.tier", 0]},
                    "stack": {"$arrayElemAt": ["$pod_info.stack", 0]},
                    "business_unit": {"$arrayElemAt": ["$pod_info.business_unit", 0]},
                    "pod_name": {"$arrayElemAt": ["$pod_info.pod_name", 0]}
                }},
                
                # Remove the pod_info array
                {"$unset": "pod_info"}
            ]
            
            results = list(self.metrics.aggregate(pipeline))
            
            if not results:
                logger.warning("No results from history aggregation pipeline")
                return pd.DataFrame()
            
            df = pd.DataFrame(results)
            
            # DEBUG: Check for duplicates in raw MongoDB data
            if 'pod_id' in df.columns and 'week_date' in df.columns:
                duplicates = df.groupby(['pod_id', 'week_date']).size()
                dup_entries = duplicates[duplicates > 1]
                if not dup_entries.empty:
                    logger.warning(f"DUPLICATES FOUND in MongoDB query results:")
                    logger.warning(f"{dup_entries}")
                    logger.warning(f"Sample duplicate data:")
                    for (pod, week), count in dup_entries.items():
                        sample = df[(df['pod_id'] == pod) & (df['week_date'] == week)]
                        logger.warning(f"  {pod} on {week}: {count} records")
                        logger.warning(f"  created_at values: {sample['created_at'].tolist() if 'created_at' in sample.columns else 'N/A'}")
            
            # Check if join worked by seeing if we have tier data
            if 'tier' not in df.columns or df['tier'].isna().all():
                logger.warning("MongoDB history join didn't work, falling back to separate queries")
                return self._get_all_history_fallback(limit_per_pod)
            
            # Remove MongoDB _id field
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            logger.info(f"Successfully joined {len(df)} history records with pod metadata")
            return df
            
        except Exception as e:
            logger.error(f"Error in get_all_history aggregation: {e}")
            return self._get_all_history_fallback(limit_per_pod)
    
    def _get_all_history_fallback(self, limit_per_pod: int = 52) -> pd.DataFrame:
        """
        Fallback method to get all history and pod info separately then merge.
        """
        try:
            # Get all metrics without join
            # Group by pod_id AND week_date to get unique records per week
            pipeline = [
                {"$sort": {"pod_id": 1, "week_date": -1, "created_at": -1}},
                # First group by pod_id and week_date to get latest record for each week
                {"$group": {
                    "_id": {"pod_id": "$pod_id", "week_date": "$week_date"},
                    "latest": {"$first": "$$ROOT"}
                }},
                {"$replaceRoot": {"newRoot": "$latest"}},
                # Then group by pod_id to limit records per pod
                {"$sort": {"pod_id": 1, "week_date": -1}},
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
            
            metrics_results = list(self.metrics.aggregate(pipeline))
            if not metrics_results:
                return pd.DataFrame()
            
            metrics_df = pd.DataFrame(metrics_results)
            
            # Get all pod info
            pods_results = list(self.pods.find({}))
            if not pods_results:
                logger.warning("No pods found in pods collection for history")
                return metrics_df
            
            pods_df = pd.DataFrame(pods_results)
            
            # Merge on pod_id
            merged_df = metrics_df.merge(
                pods_df[['pod_id', 'pod_name', 'tier', 'stack', 'business_unit']], 
                on='pod_id', 
                how='left'
            )
            
            # Remove MongoDB _id fields
            for col in ['_id_x', '_id_y', '_id']:
                if col in merged_df.columns:
                    merged_df = merged_df.drop(col, axis=1)
            
            logger.info(f"Fallback history merge successful: {len(merged_df)} records")
            return merged_df
            
        except Exception as e:
            logger.error(f"Error in history fallback method: {e}")
            return pd.DataFrame()
    
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
