"""
GitHub API Client
=================

Client for interacting with GitHub API for repository hygiene analysis.

This module provides functionality to:
    - Check repository health (stale branches, large PRs, unreviewed PRs)
    - Analyze repository structure
    - Collect evidence files for documentation generation

Example:
    >>> from src.api.github import GitHubClient
    >>> client = GitHubClient(token="your_github_token")
    >>> hygiene = client.calculate_hygiene_score("org/repo")

Author: DevOps Transformation Team
"""

import requests
import logging
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import urllib3

# Disable SSL warnings for enterprise GitHub
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure module logger
logger = logging.getLogger(__name__)


class GitHubClient:
    """
    Client for GitHub API interactions.
    
    Provides methods for repository analysis, hygiene scoring, and
    evidence collection for documentation generation.
    
    Supports both public GitHub and enterprise GitHub instances.
    
    Attributes:
        DEFAULT_BASE_URL (str): Default GitHub API base URL
        STALE_BRANCH_DAYS (int): Days after which a branch is considered stale
        LARGE_PR_LINES (int): Line count threshold for large PRs
        UNREVIEWED_PR_HOURS (int): Hours threshold for unreviewed PRs
        
    Example:
        >>> client = GitHubClient("ghp_your_token_here")
        >>> score = client.calculate_hygiene_score("myorg/myrepo")
    """
    
    # Configuration Constants
    DEFAULT_BASE_URL = "https://api.github.com"
    ENTERPRISE_API_SUFFIX = "/api/v3"  # Enterprise GitHub API path
    STALE_BRANCH_DAYS = 30
    LARGE_PR_LINES = 500
    UNREVIEWED_PR_HOURS = 24
    
    # Scoring Penalties
    PENALTY_STALE_BRANCH = 5
    PENALTY_LARGE_PR = 10
    PENALTY_UNREVIEWED_PR = 15
    
    def __init__(self, token: str, base_url: str = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token or app token.
                  Requires repo read permissions.
            base_url: Optional base URL for enterprise GitHub.
                     e.g., "https://alm-github.systems.uk.hsbc"
        
        Raises:
            ValueError: If token is empty or None.
        """
        if not token:
            raise ValueError("GitHub token is required")
            
        self.token = token
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'dpi-gamification-hygiene-checker',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        logger.info(f"GitHub client initialized with base URL: {self.base_url}")
    
    def _get_api_url(self, repo_full_name: str = None, full_url: str = None) -> str:
        """
        Determine the correct API base URL for a repository.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            full_url: Original full URL from registry (if available).
            
        Returns:
            API base URL to use for requests.
        """
        # If we have a full URL, extract the host and build API URL
        if full_url:
            import re
            match = re.match(r'https?://([^/]+)', full_url)
            if match:
                host = match.group(1)
                # Check if it's enterprise GitHub (not github.com)
                if 'github.com' not in host:
                    api_url = f"https://{host}{self.ENTERPRISE_API_SUFFIX}"
                    logger.debug(f"Using enterprise API URL: {api_url}")
                    return api_url
        
        return self.base_url
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Dict = None,
        api_base: str = None
    ) -> Tuple[int, Dict]:
        """
        Make authenticated API request with error handling.
        
        Args:
            endpoint: API endpoint path (without base URL).
            params: Optional query parameters.
            api_base: Optional API base URL (for enterprise GitHub).
            
        Returns:
            Tuple of (status_code, response_data).
        """
        base = api_base or self.base_url
        try:
            url = f"{base}/{endpoint}"
            logger.debug(f"GitHub API request: GET {url}")
            response = requests.get(
                url,
                headers=self.headers,
                params=params or {},
                verify=False,
                timeout=30
            )
            logger.debug(f"GitHub API response: {response.status_code}")
            
            if response.ok:
                return response.status_code, response.json()
            else:
                # Log error response for debugging
                logger.warning(f"GitHub API error {response.status_code} for {endpoint}")
                try:
                    error_body = response.json()
                    logger.warning(f"GitHub API error body: {error_body}")
                except:
                    pass
                return response.status_code, {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed for {url}: {e}")
            return 500, {}
    
    def get_repository_info(self, repo_full_name: str) -> Optional[Dict]:
        """
        Get repository metadata.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            
        Returns:
            Repository info dict or None if not found.
        """
        status, data = self._make_request(f"repos/{repo_full_name}")
        
        if status == 200:
            return data
        
        logger.warning(f"Could not fetch repo info for {repo_full_name}: {status}")
        return None
    
    def get_branches(self, repo_full_name: str, api_base: str = None) -> List[Dict]:
        """
        Get all branches for a repository.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            api_base: Optional API base URL for enterprise GitHub.
            
        Returns:
            List of branch dictionaries.
        """
        status, data = self._make_request(
            f"repos/{repo_full_name}/branches",
            params={'per_page': 100},
            api_base=api_base
        )
        
        if status == 200 and isinstance(data, list):
            return data
        
        logger.warning(f"[HYGIENE] Failed to get branches for {repo_full_name}: status={status}")
        return []
    
    def get_open_pull_requests(self, repo_full_name: str, api_base: str = None) -> List[Dict]:
        """
        Get all open pull requests for a repository.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            api_base: Optional API base URL for enterprise GitHub.
            
        Returns:
            List of PR dictionaries.
        """
        status, data = self._make_request(
            f"repos/{repo_full_name}/pulls",
            params={'state': 'open', 'per_page': 100},
            api_base=api_base
        )
        
        if status == 200 and isinstance(data, list):
            return data
        
        logger.warning(f"[HYGIENE] Failed to get PRs for {repo_full_name}: status={status}")
        return []
    
    def get_repository_tree(
        self, 
        repo_full_name: str, 
        branch: str = "main"
    ) -> List[str]:
        """
        Get repository file tree.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            branch: Branch name to get tree from.
            
        Returns:
            List of file paths in the repository.
        """
        status, data = self._make_request(
            f"repos/{repo_full_name}/git/trees/{branch}",
            params={'recursive': '1'}
        )
        
        if status == 200 and 'tree' in data:
            return [
                item['path'] 
                for item in data['tree'] 
                if item['type'] == 'blob'
            ]
        
        return []
    
    def get_file_content(
        self, 
        repo_full_name: str, 
        file_path: str, 
        branch: str = "main"
    ) -> Optional[str]:
        """
        Get content of a specific file.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            file_path: Path to file within repository.
            branch: Branch to read from.
            
        Returns:
            File content as string, or None if not found.
        """
        status, data = self._make_request(
            f"repos/{repo_full_name}/contents/{file_path}",
            params={'ref': branch}
        )
        
        if status == 200 and data.get('encoding') == 'base64':
            try:
                content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                return content
            except Exception as e:
                logger.error(f"Error decoding file content: {e}")
        
        return None
    
    def count_stale_branches(self, repo_full_name: str, api_base: str = None) -> int:
        """
        Count branches with no recent commits.
        
        A branch is considered stale if it has no commits in the
        last STALE_BRANCH_DAYS days.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            api_base: Optional API base URL for enterprise GitHub.
            
        Returns:
            Count of stale branches.
        """
        logger.info(f"[HYGIENE] Counting stale branches for {repo_full_name}")
        logger.info(f"[HYGIENE] Cutoff: branches with no commits in last {self.STALE_BRANCH_DAYS} days")
        
        branches = self.get_branches(repo_full_name, api_base)
        stale_count = 0
        active_count = 0
        error_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.STALE_BRANCH_DAYS)
        
        logger.info(f"[HYGIENE] Found {len(branches)} total branches in {repo_full_name}")
        logger.info(f"[HYGIENE] Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}")
        
        for branch in branches:
            branch_name = branch.get('name', '')
            if not branch_name:
                continue
            
            # Get last commit date for branch
            status, commit_data = self._make_request(
                f"repos/{repo_full_name}/commits",
                params={'sha': branch_name, 'per_page': 1},
                api_base=api_base
            )
            
            # Check if we got valid commit data (must be a non-empty list)
            if status != 200 or not isinstance(commit_data, list) or len(commit_data) == 0:
                logger.warning(f"[HYGIENE] Could not get commits for branch '{branch_name}': status={status}")
                error_count += 1
                continue
            
            # Extract commit date
            commit_date_str = commit_data[0].get('commit', {}).get('committer', {}).get('date', '')
            if not commit_date_str:
                logger.warning(f"[HYGIENE] No commit date found for branch '{branch_name}'")
                error_count += 1
                continue
            
            try:
                # Parse the ISO format date
                commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
                commit_date_naive = commit_date.replace(tzinfo=None)
                
                if commit_date_naive < cutoff_date:
                    stale_count += 1
                    logger.debug(f"[HYGIENE] STALE branch: '{branch_name}' (last commit: {commit_date_str})")
                else:
                    active_count += 1
                    logger.debug(f"[HYGIENE] ACTIVE branch: '{branch_name}' (last commit: {commit_date_str})")
                    
            except ValueError as e:
                logger.warning(f"[HYGIENE] Could not parse date '{commit_date_str}' for branch '{branch_name}': {e}")
                error_count += 1
        
        logger.info(f"[HYGIENE] Branch summary for {repo_full_name}:")
        logger.info(f"[HYGIENE]   Active (recent commits): {active_count}")
        logger.info(f"[HYGIENE]   Stale (no commits in {self.STALE_BRANCH_DAYS} days): {stale_count}")
        logger.info(f"[HYGIENE]   Errors (could not check): {error_count}")
        
        return stale_count
    
    def count_large_prs(self, repo_full_name: str, api_base: str = None) -> int:
        """
        Count PRs exceeding the line change threshold.
        
        Large PRs are harder to review and more likely to introduce bugs.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            api_base: Optional API base URL for enterprise GitHub.
            
        Returns:
            Count of large PRs.
        """
        logger.info(f"[HYGIENE] Counting large PRs for {repo_full_name}")
        prs = self.get_open_pull_requests(repo_full_name, api_base)
        large_count = 0
        
        logger.info(f"[HYGIENE] Found {len(prs)} open PRs in {repo_full_name}")
        
        for pr in prs:
            additions = pr.get('additions', 0) or 0
            deletions = pr.get('deletions', 0) or 0
            total_changes = additions + deletions
            
            if total_changes > self.LARGE_PR_LINES:
                large_count += 1
                logger.debug(f"[HYGIENE] Large PR #{pr.get('number')}: {total_changes} lines changed")
        
        logger.info(f"[HYGIENE] Large PRs in {repo_full_name}: {large_count}")
        return large_count
    
    def count_unreviewed_prs(self, repo_full_name: str, api_base: str = None) -> int:
        """
        Count PRs without reviews past the threshold.
        
        PRs should be reviewed promptly to maintain code quality.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            api_base: Optional API base URL for enterprise GitHub.
            
        Returns:
            Count of unreviewed PRs.
        """
        logger.info(f"[HYGIENE] Counting unreviewed PRs for {repo_full_name}")
        prs = self.get_open_pull_requests(repo_full_name, api_base)
        unreviewed_count = 0
        cutoff_time = datetime.now() - timedelta(hours=self.UNREVIEWED_PR_HOURS)
        
        for pr in prs:
            created_at_str = pr.get('created_at', '')
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    if created_at.replace(tzinfo=None) < cutoff_time:
                        # Check if PR has reviews
                        pr_number = pr.get('number')
                        status, reviews = self._make_request(
                            f"repos/{repo_full_name}/pulls/{pr_number}/reviews",
                            api_base=api_base
                        )
                        if status == 200 and len(reviews) == 0:
                            unreviewed_count += 1
                            logger.debug(f"[HYGIENE] Unreviewed PR #{pr_number} (created: {created_at_str})")
                except ValueError:
                    pass
        
        logger.info(f"[HYGIENE] Unreviewed PRs in {repo_full_name}: {unreviewed_count}")
        return unreviewed_count
    
    def calculate_hygiene_score(self, repo_full_name: str, full_url: str = None) -> Dict:
        """
        Calculate overall Git hygiene score for a repository.
        
        Score starts at 100 and deductions are made for:
        - Stale branches: -5 points each
        - Large PRs: -10 points each
        - Unreviewed PRs: -15 points each
        
        Args:
            repo_full_name: Full repository name (org/repo).
            full_url: Optional full URL from registry (for enterprise GitHub).
            
        Returns:
            Dictionary with score and violation counts:
            {
                'score': float,      # 0-100 score
                'critical': int,     # Critical violations (unreviewed PRs)
                'warnings': int,     # Warnings (stale branches, large PRs)
                'details': dict      # Breakdown of issues
            }
        """
        logger.info("=" * 60)
        logger.info(f"[HYGIENE] Starting hygiene score calculation")
        logger.info(f"[HYGIENE] Repository: {repo_full_name}")
        if full_url:
            logger.info(f"[HYGIENE] Full URL: {full_url}")
        
        # Determine API base URL (handles enterprise GitHub)
        api_base = self._get_api_url(repo_full_name, full_url)
        logger.info(f"[HYGIENE] Using API base: {api_base}")
        
        # Count violations
        stale_branches = self.count_stale_branches(repo_full_name, api_base)
        large_prs = self.count_large_prs(repo_full_name, api_base)
        unreviewed_prs = self.count_unreviewed_prs(repo_full_name, api_base)
        
        # Calculate score
        score = 100.0
        score -= stale_branches * self.PENALTY_STALE_BRANCH
        score -= large_prs * self.PENALTY_LARGE_PR
        score -= unreviewed_prs * self.PENALTY_UNREVIEWED_PR
        
        # Ensure score is within bounds
        score = max(0.0, min(100.0, score))
        
        # Categorize violations
        critical = unreviewed_prs  # Unreviewed PRs are critical
        warnings = stale_branches + large_prs
        
        result = {
            'score': round(score, 2),
            'critical': critical,
            'warnings': warnings,
            'details': {
                'stale_branches': stale_branches,
                'large_prs': large_prs,
                'unreviewed_prs': unreviewed_prs
            }
        }
        
        logger.info(f"[HYGIENE] === SCORE SUMMARY for {repo_full_name} ===")
        logger.info(f"[HYGIENE]   Stale branches: {stale_branches} (penalty: -{stale_branches * self.PENALTY_STALE_BRANCH})")
        logger.info(f"[HYGIENE]   Large PRs: {large_prs} (penalty: -{large_prs * self.PENALTY_LARGE_PR})")
        logger.info(f"[HYGIENE]   Unreviewed PRs: {unreviewed_prs} (penalty: -{unreviewed_prs * self.PENALTY_UNREVIEWED_PR})")
        logger.info(f"[HYGIENE]   FINAL SCORE: {score}")
        logger.info("=" * 60)
        
        return result
    
    def analyze_docs_state(self, tree_paths: List[str]) -> Dict:
        """
        Analyze existing documentation state in repository.
        
        Args:
            tree_paths: List of file paths in repository.
            
        Returns:
            Dictionary with documentation state:
            {
                'has_readme': bool,
                'has_docs_folder': bool,
                'existing_docs': list
            }
        """
        has_readme = any(
            path.lower() == 'readme.md' 
            for path in tree_paths
        )
        
        has_docs_folder = any(
            path.startswith('docs/') 
            for path in tree_paths
        )
        
        existing_docs = [
            path for path in tree_paths 
            if path.startswith('docs/') and path.endswith('.md')
        ]
        
        return {
            'has_readme': has_readme,
            'has_docs_folder': has_docs_folder,
            'existing_docs': existing_docs
        }
    
    def collect_evidence_files(
        self, 
        repo_full_name: str, 
        branch: str = "main",
        max_files: int = 10
    ) -> List[Dict]:
        """
        Collect key evidence files for repository analysis.
        
        Prioritizes important files like README, package.json,
        Dockerfile, etc. for documentation generation.
        
        Args:
            repo_full_name: Full repository name (org/repo).
            branch: Branch to collect from.
            max_files: Maximum number of files to collect.
            
        Returns:
            List of dicts with 'path' and 'content' keys.
        """
        # Priority patterns for evidence collection
        priority_patterns = [
            r'^README\.md$',
            r'^package\.json$',
            r'^pom\.xml$',
            r'^build\.gradle$',
            r'^requirements\.txt$',
            r'^Dockerfile$',
            r'^docker-compose\.ya?ml$',
            r'^\.github/workflows/.*\.ya?ml$',
            r'^src/main/.*\.java$',
            r'^src/.*\.py$',
            r'^.*\.config\.js$'
        ]
        
        # Get repository tree
        tree_paths = self.get_repository_tree(repo_full_name, branch)
        evidence_files = []
        
        for pattern in priority_patterns:
            if len(evidence_files) >= max_files:
                break
            
            pattern_re = re.compile(pattern, re.IGNORECASE)
            matching_paths = [p for p in tree_paths if pattern_re.search(p)]
            
            for path in matching_paths[:2]:  # Max 2 files per pattern
                if len(evidence_files) >= max_files:
                    break
                
                content = self.get_file_content(repo_full_name, path, branch)
                if content:
                    # Truncate large files
                    if len(content) > 5000:
                        content = content[:5000] + "\n... (truncated)"
                    
                    evidence_files.append({
                        'path': path,
                        'content': content
                    })
        
        logger.info(f"Collected {len(evidence_files)} evidence files from {repo_full_name}")
        return evidence_files
