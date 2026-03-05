"""
API Integration Module for TeamBook and DataSight APIs
Handles fetching pod details and metrics (MTTR, LTTD, RF, CFR)
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TeamBookAPI:
    """Handles TeamBook API interactions"""
    
    BASE_URL = "https://api-teambook.global.hsbc"
    SERVICE_LINE_ID = 449
    
    def __init__(self, bearer_token: str):
        """
        Initialize TeamBook API client
        
        Args:
            bearer_token: Bearer token for authentication
        """
        self.bearer_token = bearer_token
        self.headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {bearer_token}'
        }
    
    def get_pods(self) -> List[Dict]:
        """
        Fetch all pods under the service line
        
        Returns:
            List of dictionaries containing pod_id and pod_name
        """
        try:
            url = f"{self.BASE_URL}/pod?serviceline={self.SERVICE_LINE_ID}"
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            pods = []
            if 'child' in data:
                for pod in data['child']:
                    pods.append({
                        'pod_id': pod.get('Pod ID'),
                        'pod_name': pod.get('Pod')
                    })
            
            logger.info(f"Fetched {len(pods)} pods from TeamBook")
            return pods
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching pods from TeamBook: {e}")
            raise


class DataSightAPI:
    """Handles DataSight API interactions for metrics"""
    
    BASE_URL = "https://datasight.global.hsbc"
    TEAMBOOK_LEVEL = 5
    PAGE_SIZE = 50
    
    def __init__(self, bearer_token: str):
        """
        Initialize DataSight API client
        
        Args:
            bearer_token: Bearer token for authentication
        """
        self.bearer_token = bearer_token
        self.headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {bearer_token}'
        }
    
    def _format_date(self, date: datetime) -> str:
        """Format date to YYYY-MM format"""
        return date.strftime('%Y-%m')
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Make API request with error handling
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data
        """
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from {endpoint}: {e}")
            return {}
    
    def get_mttr(self, pod_id: int, from_date: datetime, to_date: datetime) -> Optional[float]:
        """
        Fetch MTTR (Mean Time To Restore) metric
        
        Args:
            pod_id: TeamBook pod ID
            from_date: Start date
            to_date: End date
            
        Returns:
            MTTR value or None
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookIds': pod_id,
            'teambookLevel': self.TEAMBOOK_LEVEL,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request('incident/metric/mttr/by-group/teambook/metric', params)
        
        if data and 'items' in data and len(data['items']) > 0:
            return data['items'][0].get('mttr')  # API returns 'mttr'
        return None
    
    def get_lttd(self, pod_id: int, from_date: datetime, to_date: datetime) -> Optional[float]:
        """
        Fetch LTTD (Lead Time To Deploy) metric
        
        Args:
            pod_id: TeamBook pod ID
            from_date: Start date
            to_date: End date
            
        Returns:
            LTTD value or None
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookIds': pod_id,
            'teambookLevel': self.TEAMBOOK_LEVEL,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request('releases/metric/lttd/teambook/metric', params)
        
        if data and 'items' in data and len(data['items']) > 0:
            return data['items'][0].get('lttd')  # API returns 'lttd'
        return None
    
    def get_release_frequency(self, pod_id: int, from_date: datetime, to_date: datetime) -> Optional[int]:
        """
        Fetch Release Frequency metric
        
        Args:
            pod_id: TeamBook pod ID
            from_date: Start date
            to_date: End date
            
        Returns:
            Release Frequency value or None
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookIds': pod_id,
            'teambookLevel': self.TEAMBOOK_LEVEL,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request('releases/metric/release-frequency/teambook/metric', params)
        
        if data and 'items' in data and len(data['items']) > 0:
            return data['items'][0].get('releases')  # API returns 'releases' for release frequency
        return None
    
    def get_cfr(self, pod_id: int, from_date: datetime, to_date: datetime) -> Optional[float]:
        """
        Fetch CFR (Change Failure Rate) metric
        
        Args:
            pod_id: TeamBook pod ID
            from_date: Start date
            to_date: End date
            
        Returns:
            CFR value or None
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookIds': pod_id,
            'teambookLevel': self.TEAMBOOK_LEVEL,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request('releases/metric/cfr/teambook/metric', params)
        
        if data and 'items' in data and len(data['items']) > 0:
            return data['items'][0].get('change_failure_rate')  # API returns 'change_failure_rate'
        return None
    
    def get_all_metrics(self, pod_id: int, from_date: datetime, to_date: datetime) -> Dict:
        """
        Fetch all metrics for a pod
        
        Args:
            pod_id: TeamBook pod ID
            from_date: Start date
            to_date: End date
            
        Returns:
            Dictionary containing all metrics
        """
        return {
            'mttr': self.get_mttr(pod_id, from_date, to_date),
            'lttd': self.get_lttd(pod_id, from_date, to_date),
            'rf': self.get_release_frequency(pod_id, from_date, to_date),
            'cfr': self.get_cfr(pod_id, from_date, to_date)
        }


class MetricsCollector:
    """Orchestrates data collection from TeamBook and DataSight APIs"""
    
    def __init__(self, teambook_token: str, datasight_token: str = None):
        """
        Initialize metrics collector
        
        Args:
            teambook_token: Bearer token for TeamBook API
            datasight_token: Bearer token for DataSight API (optional, defaults to teambook_token)
        """
        self.teambook = TeamBookAPI(teambook_token)
        self.datasight = DataSightAPI(datasight_token or teambook_token)
    
    def collect_weekly_metrics(self, week_date: datetime) -> List[Dict]:
        """
        Collect metrics for all pods for a specific week
        
        Args:
            week_date: Date representing the week (YYYY-MM format)
            
        Returns:
            List of dictionaries containing pod metrics
        """
        pods = self.teambook.get_pods()
        metrics_data = []
        
        for pod in pods:
            pod_id = pod['pod_id']
            pod_name = pod['pod_name']
            
            logger.info(f"Fetching metrics for pod: {pod_name} (ID: {pod_id})")
            
            metrics = self.datasight.get_all_metrics(pod_id, week_date, week_date)
            
            metrics_data.append({
                'pod_id': pod_id,
                'pod_name': pod_name,
                'week_date': week_date,
                'mttr': metrics.get('mttr'),
                'lttd': metrics.get('lttd'),
                'rf': metrics.get('rf'),
                'cfr': metrics.get('cfr')
            })
        
        logger.info(f"Collected metrics for {len(metrics_data)} pods")
        return metrics_data
