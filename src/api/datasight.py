"""
DataSight API Client
====================

Client for interacting with the DataSight API to fetch DevOps metrics.

This module provides a clean interface to fetch:
    - MTTR (Mean Time To Restore)
    - LTTD (Lead Time To Deploy)
    - RF (Release Frequency)
    - CFR (Change Failure Rate)

Example:
    >>> from src.api.datasight import DataSightClient
    >>> client = DataSightClient(bearer_token="your_token")
    >>> metrics = client.get_all_metrics("pod_name", "5", from_date, to_date)

Author: DevOps Transformation Team
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional

import urllib3

# Disable SSL warnings for internal APIs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure module logger
logger = logging.getLogger(__name__)


class DataSightClient:
    """
    Client for DataSight API interactions.
    
    Handles authentication and provides methods to fetch various DevOps metrics
    from the DataSight platform.
    
    Attributes:
        BASE_URL (str): Base URL for DataSight API
        TEAMBOOK_LEVEL (int): Default TeamBook hierarchy level
        PAGE_SIZE (int): Default pagination size for API requests
        
    Example:
        >>> client = DataSightClient("bearer_token_here")
        >>> mttr = client.get_mttr("MyPod", "5", start_date, end_date)
    """
    
    # API Configuration Constants
    BASE_URL = "https://datasight.global.hsbc"
    TEAMBOOK_LEVEL = 5
    PAGE_SIZE = 50
    
    def __init__(self, bearer_token: str):
        """
        Initialize DataSight API client.
        
        Args:
            bearer_token: Bearer token for API authentication.
                         Obtain from DataSight admin portal.
        
        Raises:
            ValueError: If bearer_token is empty or None.
        """
        if not bearer_token:
            raise ValueError("Bearer token is required for DataSight API")
            
        self.bearer_token = bearer_token
        self.headers = {
            'accept': 'text/plain',
            'Authorization': f'Bearer {bearer_token}'
        }
        logger.info("DataSight client initialized successfully")
    
    def _format_date(self, date: datetime) -> str:
        """
        Format datetime to API-required YYYY-MM format.
        
        Args:
            date: Python datetime object.
            
        Returns:
            Date string in YYYY-MM format.
        """
        return date.strftime('%Y-%m')
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Make authenticated API request with error handling.
        
        Args:
            endpoint: API endpoint path (without base URL).
            params: Query parameters dictionary.
            
        Returns:
            JSON response data as dictionary.
            Empty dict on error.
        """
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            logger.debug(f"Making request to: {url}")
            
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params, 
                verify=False,  # Internal API - SSL verification disabled
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for endpoint: {endpoint}")
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return {}
    
    def get_mttr(
        self, 
        teambook_name: str, 
        teambook_level: str, 
        from_date: datetime, 
        to_date: datetime
    ) -> Optional[float]:
        """
        Fetch MTTR (Mean Time To Restore) metric.
        
        MTTR measures the average time to restore service after an incident.
        Lower values indicate better incident response capabilities.
        
        Args:
            teambook_name: TeamBook pod/team name.
            teambook_level: TeamBook hierarchy level (typically "5").
            from_date: Start date for metric period.
            to_date: End date for metric period.
            
        Returns:
            MTTR value in hours, or 0 if not available.
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookNames': teambook_name,
            'teambookLevel': teambook_level,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request(
            'incident/metric/mttr/by-group/teambook/metric', 
            params
        )
        
        # Extract MTTR value from response
        if data and 'data' in data and len(data['data']) > 0:
            mttr_value = data['data'][0].get('mttr')
            logger.debug(f"MTTR for {teambook_name}: {mttr_value}")
            return mttr_value if mttr_value is not None else 0
        
        logger.debug(f"No MTTR data found for {teambook_name}")
        return 0
    
    def get_lttd(
        self, 
        teambook_name: str, 
        teambook_level: str, 
        from_date: datetime, 
        to_date: datetime
    ) -> Optional[float]:
        """
        Fetch LTTD (Lead Time To Deploy) metric.
        
        LTTD measures the time from code commit to production deployment.
        Lower values indicate faster delivery pipelines.
        
        Args:
            teambook_name: TeamBook pod/team name.
            teambook_level: TeamBook hierarchy level.
            from_date: Start date for metric period.
            to_date: End date for metric period.
            
        Returns:
            LTTD value in days, or 0 if not available.
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookNames': teambook_name,
            'teambookLevel': teambook_level,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request(
            'releases/metric/lttd/teambook/metric', 
            params
        )
        
        if data and 'data' in data and len(data['data']) > 0:
            lttd_value = data['data'][0].get('lttd')
            logger.debug(f"LTTD for {teambook_name}: {lttd_value}")
            return lttd_value if lttd_value is not None else 0
        
        logger.debug(f"No LTTD data found for {teambook_name}")
        return 0
    
    def get_release_frequency(
        self, 
        teambook_name: str, 
        teambook_level: str, 
        from_date: datetime, 
        to_date: datetime
    ) -> Optional[int]:
        """
        Fetch Release Frequency (RF) metric.
        
        RF measures the number of production deployments in a period.
        Higher values indicate more frequent, smaller releases.
        
        Args:
            teambook_name: TeamBook pod/team name.
            teambook_level: TeamBook hierarchy level.
            from_date: Start date for metric period.
            to_date: End date for metric period.
            
        Returns:
            Release count (ytd_pdptppy_basis), or 0 if not available.
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookNames': teambook_name,
            'teambookLevel': teambook_level,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request(
            'releases/metric/release-frequency/teambook/metric', 
            params
        )
        
        if data and 'data' in data and len(data['data']) > 0:
            # Primary: ytd_pdptppy_basis, Fallback: releases count
            rf_value = data['data'][0].get('ytd_pdptppy_basis')
            if rf_value is None:
                rf_value = data['data'][0].get('releases')
            
            logger.debug(f"RF for {teambook_name}: {rf_value}")
            return rf_value if rf_value is not None else 0
        
        logger.debug(f"No RF data found for {teambook_name}")
        return 0
    
    def get_cfr(
        self, 
        teambook_name: str, 
        teambook_level: str, 
        from_date: datetime, 
        to_date: datetime
    ) -> Optional[float]:
        """
        Fetch CFR (Change Failure Rate) metric.
        
        CFR measures the percentage of deployments causing failures.
        Lower values indicate more stable releases.
        
        Args:
            teambook_name: TeamBook pod/team name.
            teambook_level: TeamBook hierarchy level.
            from_date: Start date for metric period.
            to_date: End date for metric period.
            
        Returns:
            CFR percentage value, or 0 if not available.
        """
        params = {
            'from': self._format_date(from_date),
            'to': self._format_date(to_date),
            'teambookNames': teambook_name,
            'teambookLevel': teambook_level,
            'page': 1,
            'size': self.PAGE_SIZE
        }
        
        data = self._make_request(
            'releases/metric/cfr/teambook/metric', 
            params
        )
        
        if data and 'data' in data and len(data['data']) > 0:
            cfr_value = data['data'][0].get('change_failure_rate')
            logger.debug(f"CFR for {teambook_name}: {cfr_value}")
            return cfr_value if cfr_value is not None else 0
        
        logger.debug(f"No CFR data found for {teambook_name}")
        return 0
    
    def get_all_metrics(
        self, 
        teambook_name: str, 
        teambook_level: str, 
        from_date: datetime, 
        to_date: datetime
    ) -> Dict[str, Optional[float]]:
        """
        Fetch all DORA metrics for a pod in a single call.
        
        Convenience method that retrieves all four key metrics:
        MTTR, LTTD, RF, and CFR.
        
        Args:
            teambook_name: TeamBook pod/team name.
            teambook_level: TeamBook hierarchy level.
            from_date: Start date for metric period.
            to_date: End date for metric period.
            
        Returns:
            Dictionary containing all metrics:
            {
                'mttr': float,  # Mean Time To Restore (hours)
                'lttd': float,  # Lead Time To Deploy (days)
                'rf': int,      # Release Frequency (count)
                'cfr': float    # Change Failure Rate (percentage)
            }
        """
        logger.info(f"Fetching all metrics for: {teambook_name}")
        
        return {
            'mttr': self.get_mttr(teambook_name, teambook_level, from_date, to_date),
            'lttd': self.get_lttd(teambook_name, teambook_level, from_date, to_date),
            'rf': self.get_release_frequency(teambook_name, teambook_level, from_date, to_date),
            'cfr': self.get_cfr(teambook_name, teambook_level, from_date, to_date)
        }
