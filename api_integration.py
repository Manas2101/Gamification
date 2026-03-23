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

# Disable SSL warnings when verify=False is used
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
    
    def __init__(self, datasight_token: str, registry_dir: str = None, github_token: str = None):
        """
        Initialize metrics collector
        
        Args:
            datasight_token: Bearer token for DataSight API
            registry_dir: Path to YAML registry directory (optional)
            github_token: GitHub token for hygiene checking (optional)
        """
        self.datasight = DataSightAPI(datasight_token)
        self.github_token = github_token
        
        # Import here to avoid circular dependency
        from registry_loader import RegistryLoader
        self.registry = RegistryLoader(registry_dir)
    
    def _calculate_git_hygiene_score(self, app) -> Dict:
        """
        Calculate basic git hygiene score for an app
        
        Simple scoring based on:
        - Stale branches (>30 days without commits)
        - Large PRs (>500 lines)
        - Unreviewed PRs (>24 hours)
        
        Args:
            app: AppEntry object with repo information
        
        Returns:
            Dict with score, critical_count, warning_count
        """
        if not self.github_token:
            logger.warning(f"No GitHub token configured for {app.app_name} - returning default score 100")
            return {
                'score': 100.0,
                'critical': 0,
                'warnings': 0,
                'note': 'No GitHub token configured'
            }
        
        if not app.repos:
            logger.warning(f"No repos defined in YAML for {app.app_name} - returning default score 100")
            return {
                'score': 100.0,
                'critical': 0,
                'warnings': 0,
                'note': 'No repos defined in YAML'
            }
        
        try:
            import requests
            score = 100.0
            critical_count = 0
            warning_count = 0
            
            # Debug: Show token configuration (first/last 4 chars only for security)
            if self.github_token:
                token_preview = f"{self.github_token[:4]}...{self.github_token[-4:]}" if len(self.github_token) > 8 else "***"
                logger.debug(f"GitHub token configured: {token_preview} (length: {len(self.github_token)})")
            else:
                logger.warning(f"GitHub token is empty or None")
            
            # CORRECT GitHub API token format with required headers
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'dpi-gamification-hygiene-checker',
                'X-GitHub-Api-Version': '2022-11-28'
            }
            
            # Check primary repo only (to keep it fast)
            primary_repo = app.primary_repo
            if not primary_repo:
                logger.warning(f"No primary repo found for {app.app_name} - returning default score 100")
                return {'score': 100.0, 'critical': 0, 'warnings': 0}
            
            # Check if repo fields are actually filled
            if not primary_repo.git_org or not primary_repo.repo_name:
                logger.warning(f"Primary repo has empty git_org or repo_name for {app.app_name} - returning default score 100")
                return {'score': 100.0, 'critical': 0, 'warnings': 0}
            
            # Use the repo's api_base_url property which automatically converts Git URL to API URL
            base_url = primary_repo.api_base_url
            repo_full_name = primary_repo.full_name
            
            logger.info(f"Checking Git hygiene for {app.app_name} repo: {repo_full_name}")
            logger.debug(f"Using API URL: {base_url}")
            if primary_repo.original_url:
                logger.debug(f"Original Git URL: {primary_repo.original_url}")
            
            # Check 1: Stale branches (deduct 5 points per stale branch, max 3 checks)
            try:
                branches_resp = requests.get(f"{base_url}/branches", headers=headers, timeout=10, verify=False)
                if branches_resp.status_code == 200:
                    branches = branches_resp.json()[:3]  # Check only first 3 branches
                    cutoff_date = datetime.now() - timedelta(days=30)
                    
                    for branch in branches:
                        if branch['name'] in ['main', 'master']:
                            continue
                        
                        # Get last commit date
                        commit_resp = requests.get(f"{base_url}/commits/{branch['commit']['sha']}", headers=headers, timeout=10, verify=False)
                        if commit_resp.status_code == 200:
                            commit_date_str = commit_resp.json()['commit']['committer']['date']
                            commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ')
                            
                            if commit_date < cutoff_date:
                                score -= 5
                                warning_count += 1
                                logger.info(f"  Found stale branch '{branch['name']}' (last commit: {commit_date_str})")
                elif branches_resp.status_code == 404:
                    logger.warning(f"Repository not found: {repo_full_name} - check git_org and repo_name in YAML")
                elif branches_resp.status_code == 401:
                    logger.error(f"GitHub authentication failed (401) for {repo_full_name}")
                    logger.error(f"  API URL: {base_url}/branches")
                    logger.error(f"  Token present: {bool(self.github_token)}")
                    logger.error(f"  Token length: {len(self.github_token) if self.github_token else 0}")
                    logger.error(f"  Response: {branches_resp.text}")
                    logger.error(f"  Headers sent: Authorization=token ***{self.github_token[-4:] if self.github_token and len(self.github_token) > 4 else '****'}")
                else:
                    logger.warning(f"GitHub API error for {repo_full_name}: {branches_resp.status_code} - {branches_resp.text}")
            except Exception as e:
                logger.warning(f"Error checking branches for {repo_full_name}: {e}")
            
            # Check 2: Large/Unreviewed PRs (deduct 10 points per issue, max 2 checks)
            try:
                prs_resp = requests.get(f"{base_url}/pulls?state=open&per_page=2", headers=headers, timeout=10, verify=False)
                if prs_resp.status_code == 200:
                    prs = prs_resp.json()
                    
                    for pr in prs:
                        # Check PR size
                        pr_size = pr.get('additions', 0) + pr.get('deletions', 0)
                        if pr_size > 500:
                            score -= 10
                            critical_count += 1
                            logger.info(f"  Found large PR #{pr['number']} ({pr_size} lines changed)")
                        
                        # Check review status
                        created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                        age_hours = (datetime.now() - created_at).total_seconds() / 3600
                        
                        if age_hours > 24:
                            reviews_resp = requests.get(f"{base_url}/pulls/{pr['number']}/reviews", headers=headers, timeout=10, verify=False)
                            if reviews_resp.status_code == 200 and len(reviews_resp.json()) == 0:
                                score -= 5
                                warning_count += 1
                                logger.info(f"  Found unreviewed PR #{pr['number']} (open for {age_hours:.1f} hours)")
            except Exception as e:
                logger.warning(f"Error checking PRs for {repo_full_name}: {e}")
            
            final_score = max(0.0, score)
            logger.info(f"  Final Git Hygiene score for {app.app_name}: {final_score:.1f}/100 (critical: {critical_count}, warnings: {warning_count})")
            
            return {
                'score': final_score,
                'critical': critical_count,
                'warnings': warning_count
            }
            
        except Exception as e:
            logger.error(f"Error calculating hygiene for {app.app_name}: {e}")
            return {'score': 100.0, 'critical': 0, 'warnings': 0}
    
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
            
            # Fetch DataSight metrics
            metrics = self.datasight.get_all_metrics(teambook_name, teambook_level, week_date, week_date)
            
            # Calculate git hygiene score
            hygiene = self._calculate_git_hygiene_score(app)
            logger.info(f"  Git hygiene score for {app.app_name}: {hygiene.get('score', 50.0):.1f}/100")
            
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
                # Git hygiene data
                'git_hygiene_score': hygiene.get('score'),
                'git_hygiene_violations_critical': hygiene.get('critical', 0),
                'git_hygiene_violations_warnings': hygiene.get('warnings', 0),
                # Include all YAML data for scoring
                'stack': app.stack,
                'business_unit': 'Default',  # Can be added to YAML if needed
                'tier': app.tier,
                'app_type': app.app_type,
                'ci': app.ci_automated,
                'cd': app.cd_automated,
                'iac': False,  # Can be added to YAML if needed
                'rollback': app.automated_rollback,
                'self_service': app.zero_touch_deployment,
                'zero_touch_deployment': app.zero_touch_deployment,
                'cr_auto_creation': app.cr_auto_creation,
                'feature_flags_adopted': app.feature_flags_adopted,
                'pipeline_standard': app.pipeline_standard,
                'sast_enabled': app.sast_enabled,
                'data_classification': app.data_classification,
                'release_page_url': app.release_page_url,
                'compliance_evidence_page': app.compliance_evidence_page,
                'priv_access_reviewed_date': app.priv_access_reviewed_date,
                'is_priv_access_current': app.is_priv_access_current,
                'apis_published': app.apis_published,
                'ai_tools_declared': app.ai_tools_declared,
                'copilot_enabled': app.copilot_enabled,
                'sonarqube_project': app.sonarqube_project,
            })
        
        logger.info(f"Collected metrics for {len(metrics_data)} apps")
        return metrics_data
