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
    
    def get_mttr(self, teambook_name: str, teambook_level: str, from_date: datetime, to_date: datetime) -> Optional[float]:
        """
        Fetch MTTR (Mean Time To Restore) metric
        
        Args:
            teambook_name: TeamBook pod name
            teambook_level: TeamBook pod level
            from_date: Start date
            to_date: End date
            
        Returns:
            MTTR value or None
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookNames': teambook_name,
            'teambookLevel': teambook_level,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request('incident/metric/mttr/by-group/teambook/metric', params)
        
        if data and 'data' in data and len(data['data']) > 0:
            mttr_value = data['data'][0].get('mttr')
            return mttr_value if mttr_value is not None else 0
        return 0
    
    def get_lttd(self, teambook_name: str, teambook_level: str, from_date: datetime, to_date: datetime) -> Optional[float]:
        """
        Fetch LTTD (Lead Time To Deploy) metric
        
        Args:
            teambook_name: TeamBook pod name
            teambook_level: TeamBook pod level
            from_date: Start date
            to_date: End date
            
        Returns:
            LTTD value or None
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookNames': teambook_name,
            'teambookLevel': teambook_level,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request('releases/metric/lttd/teambook/metric', params)
        
        if data and 'data' in data and len(data['data']) > 0:
            lttd_value = data['data'][0].get('lttd')
            return lttd_value if lttd_value is not None else 0
        return 0
    
    def get_release_frequency(self, teambook_name: str, teambook_level: str, from_date: datetime, to_date: datetime) -> Optional[int]:
        """
        Fetch Release Frequency metric (ytd_pdptppy_basis)
        
        Args:
            teambook_name: TeamBook pod name
            teambook_level: TeamBook pod level
            from_date: Start date
            to_date: End date
            
        Returns:
            Release Frequency value (ytd_pdptppy_basis) or None
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookNames': teambook_name,
            'teambookLevel': teambook_level,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request('releases/metric/release-frequency/teambook/metric', params)
        
        if data and 'data' in data and len(data['data']) > 0:
            # Fetch RF as ytd_pdptppy_basis from response
            rf_value = data['data'][0].get('ytd_pdptppy_basis')
            if rf_value is None:
                # Fallback to 'releases' field if ytd_pdptppy_basis not found
                rf_value = data['data'][0].get('releases')
            return rf_value if rf_value is not None else 0
        return 0
    
    def get_cfr(self, teambook_name: str, teambook_level: str, from_date: datetime, to_date: datetime) -> Optional[float]:
        """
        Fetch CFR (Change Failure Rate) metric
        
        Args:
            teambook_name: TeamBook pod name
            teambook_level: TeamBook pod level
            from_date: Start date
            to_date: End date
            
        Returns:
            CFR value or None
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookNames': teambook_name,
            'teambookLevel': teambook_level,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request('releases/metric/cfr/teambook/metric', params)
        
        if data and 'data' in data and len(data['data']) > 0:
            cfr_value = data['data'][0].get('change_failure_rate')
            return cfr_value if cfr_value is not None else 0
        return 0
    
    def get_all_metrics(self, teambook_name: str, teambook_level: str, from_date: datetime, to_date: datetime) -> Dict:
        """
        Fetch all metrics for a pod using teambook name
        
        Args:
            teambook_name: TeamBook pod name
            teambook_level: TeamBook pod level
            from_date: Start date
            to_date: End date
            
        Returns:
            Dictionary containing all metrics
        """
        return {
            'mttr': self.get_mttr(teambook_name, teambook_level, from_date, to_date),
            'lttd': self.get_lttd(teambook_name, teambook_level, from_date, to_date),
            'rf': self.get_release_frequency(teambook_name, teambook_level, from_date, to_date),
            'cfr': self.get_cfr(teambook_name, teambook_level, from_date, to_date)
        }


class MetricsCollector:
    """Orchestrates data collection from YAML registry and DataSight API"""
    
    def __init__(self, datasight_token: str, registry_dir: str = None):
        """
        Initialize metrics collector
        
        Args:
            datasight_token: Bearer token for DataSight API
            registry_dir: Path to YAML registry directory (optional)
        """
        self.datasight = DataSightAPI(datasight_token)
        
        # Import here to avoid circular dependency
        from registry_loader import RegistryLoader
        self.registry = RegistryLoader(registry_dir)
    
    def collect_weekly_metrics(self, week_date: datetime) -> List[Dict]:
        """
        Collect metrics for all apps from YAML registry
        
        Args:
            week_date: Date representing the week (YYYY-MM format)
            
        Returns:
            List of dictionaries containing app metrics
        """
        apps = self.registry.load_all()
        metrics_data = []
        
        for app in apps:
            # Get first teambook pod name (primary pod)
            if not app.teambook_pods:
                logger.warning(f"App {app.app_name} has no teambook pods defined, skipping")
                continue
            
            teambook_name = app.teambook_pods[0]
            teambook_level = app.teambook_level
            
            logger.info(f"Fetching metrics for app: {app.app_name} (EIM: {app.eim}, Pod: {teambook_name}, Level: {teambook_level})")
            
            metrics = self.datasight.get_all_metrics(teambook_name, teambook_level, week_date, week_date)
            
            metrics_data.append({
                'pod_id': app.eim,  # Use EIM as pod_id
                'pod_name': teambook_name,
                'app_name': app.app_name,
                'eim': app.eim,
                'week_date': week_date,
                'mttr': metrics.get('mttr'),
                'lttd': metrics.get('lttd'),
                'rf': metrics.get('rf'),
                'cfr': metrics.get('cfr'),
                # Include all YAML data for scoring
                'stack': app.stack,
                'business_unit': 'Default',  # Can be added to YAML if needed
                'tier': app.tier,
                'ci': app.ci_automated,
                'cd': app.cd_automated,
                'iac': False,  # Can be added to YAML if needed
                'rollback': app.automated_rollback,
                'self_service': app.zero_touch_deployment,
            })
        
        logger.info(f"Collected metrics for {len(metrics_data)} apps")
        return metrics_data
