"""
Registry Loader
===============

Loads and parses application registry from YAML files.

The registry contains application metadata including:
    - Application identifiers and names
    - Repository information
    - TeamBook pod mappings
    - Configuration flags

Example:
    >>> from src.data.registry import RegistryLoader
    >>> loader = RegistryLoader("apps/")
    >>> apps = loader.load_all_apps()

Author: DevOps Transformation Team
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

import yaml

# Configure module logger
logger = logging.getLogger(__name__)


@dataclass
class RepoInfo:
    """
    Repository information from registry.
    
    Attributes:
        git_org: GitHub organization name
        repo_name: Repository name
        full_name: Full repository path (org/repo)
    """
    git_org: str
    repo_name: str
    
    @property
    def full_name(self) -> str:
        """Get full repository name (org/repo)."""
        return f"{self.git_org}/{self.repo_name}"


@dataclass
class AppEntry:
    """
    Application entry from registry.
    
    Represents a single application with its metadata,
    repositories, and configuration.
    
    Attributes:
        app_id: Unique application identifier (EIM)
        app_name: Display name for the application
        pod_name: TeamBook pod name
        pod_level: TeamBook hierarchy level
        repos: List of associated repositories
        stack: Technology stack
        tier: Service tier
        business_unit: Business unit name
        config: Additional configuration flags
    """
    app_id: str
    app_name: str
    pod_name: str = ""
    pod_level: str = "5"
    repos: List[RepoInfo] = field(default_factory=list)
    stack: str = ""
    tier: str = ""
    business_unit: str = ""
    config: Dict = field(default_factory=dict)


class RegistryLoader:
    """
    Loader for YAML application registry.
    
    Reads YAML files from a directory and parses them into
    structured AppEntry objects.
    
    Attributes:
        registry_dir (str): Path to registry directory
        
    Example:
        >>> loader = RegistryLoader("apps/")
        >>> apps = loader.load_all_apps()
        >>> for app in apps:
        ...     print(f"{app.app_name}: {len(app.repos)} repos")
    """
    
    def __init__(self, registry_dir: str = None):
        """
        Initialize registry loader.
        
        Args:
            registry_dir: Path to directory containing YAML files.
                         Defaults to 'apps/' in current directory.
        """
        if registry_dir is None:
            # Default to 'apps' directory relative to project root
            registry_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'apps'
            )
        
        self.registry_dir = os.path.abspath(registry_dir)
        logger.info(f"Registry loader initialized: {self.registry_dir}")
    
    def _parse_repos(self, repos_data: List) -> List[RepoInfo]:
        """
        Parse repository list from YAML data.
        
        Args:
            repos_data: List of repo dictionaries from YAML.
            
        Returns:
            List of RepoInfo objects.
        """
        repos = []
        
        if not repos_data:
            return repos
        
        for repo in repos_data:
            if isinstance(repo, dict):
                git_org = repo.get('git_org', '')
                repo_name = repo.get('repo_name', '')
                
                if git_org and repo_name:
                    repos.append(RepoInfo(
                        git_org=git_org,
                        repo_name=repo_name
                    ))
        
        return repos
    
    def _parse_app_entry(self, data: Dict, file_path: str) -> Optional[AppEntry]:
        """
        Parse single application entry from YAML data.
        
        Args:
            data: Dictionary from parsed YAML.
            file_path: Source file path for logging.
            
        Returns:
            AppEntry object or None if parsing fails.
        """
        try:
            # Extract app ID from filename if not in data
            app_id = data.get('eim') or data.get('app_id')
            if not app_id:
                # Try to get from filename
                filename = os.path.basename(file_path)
                app_id = os.path.splitext(filename)[0]
            
            app_name = data.get('app_name') or data.get('name', f'App-{app_id}')
            
            # Parse repositories
            repos = self._parse_repos(data.get('repos', []))
            
            # Extract configuration flags
            config = {
                'ci': data.get('ci', False),
                'cd': data.get('cd', False),
                'rollback': data.get('rollback', False),
                'self_service': data.get('self_service', False),
                'pipeline_standard': data.get('pipeline_standard', False),
                'sast_enabled': data.get('sast_enabled', False),
                'sonarqube_project': data.get('sonarqube_project', ''),
                'data_classification': data.get('data_classification', ''),
                'copilot_enabled': data.get('copilot_enabled', False),
                'ai_tools_declared': data.get('ai_tools_declared', False),
                'apis_published': data.get('apis_published', 0),
                'feature_flags_adopted': data.get('feature_flags_adopted', False),
                'release_page_url': data.get('release_page_url', ''),
                'compliance_evidence_page': data.get('compliance_evidence_page', ''),
                'is_priv_access_current': data.get('is_priv_access_current', False),
                'cr_auto_creation': data.get('cr_auto_creation', False),
                'zero_touch_deployment': data.get('zero_touch_deployment', False)
            }
            
            return AppEntry(
                app_id=str(app_id),
                app_name=app_name,
                pod_name=data.get('pod_name', ''),
                pod_level=str(data.get('pod_level', '5')),
                repos=repos,
                stack=data.get('stack', ''),
                tier=data.get('tier', ''),
                business_unit=data.get('business_unit', ''),
                config=config
            )
            
        except Exception as e:
            logger.error(f"Error parsing app entry from {file_path}: {e}")
            return None
    
    def load_app(self, file_path: str) -> Optional[AppEntry]:
        """
        Load single application from YAML file.
        
        Args:
            file_path: Path to YAML file.
            
        Returns:
            AppEntry object or None if loading fails.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                logger.warning(f"Empty YAML file: {file_path}")
                return None
            
            return self._parse_app_entry(data, file_path)
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def load_all_apps(self) -> List[AppEntry]:
        """
        Load all applications from registry directory.
        
        Returns:
            List of AppEntry objects.
        """
        apps = []
        
        if not os.path.exists(self.registry_dir):
            logger.warning(f"Registry directory not found: {self.registry_dir}")
            return apps
        
        # Find all YAML files
        yaml_files = [
            f for f in os.listdir(self.registry_dir)
            if f.endswith(('.yaml', '.yml'))
        ]
        
        logger.info(f"Found {len(yaml_files)} YAML files in registry")
        
        for filename in yaml_files:
            file_path = os.path.join(self.registry_dir, filename)
            app = self.load_app(file_path)
            
            if app:
                apps.append(app)
                logger.debug(f"Loaded app: {app.app_name} ({app.app_id})")
        
        logger.info(f"Loaded {len(apps)} applications from registry")
        return apps
    
    def get_app_by_id(self, app_id: str) -> Optional[AppEntry]:
        """
        Get specific application by ID.
        
        Args:
            app_id: Application identifier.
            
        Returns:
            AppEntry or None if not found.
        """
        file_path = os.path.join(self.registry_dir, f"{app_id}.yaml")
        
        if os.path.exists(file_path):
            return self.load_app(file_path)
        
        # Try .yml extension
        file_path = os.path.join(self.registry_dir, f"{app_id}.yml")
        if os.path.exists(file_path):
            return self.load_app(file_path)
        
        logger.warning(f"App not found in registry: {app_id}")
        return None
    
    def get_all_repos(self) -> List[RepoInfo]:
        """
        Get all repositories from all applications.
        
        Returns:
            List of all RepoInfo objects.
        """
        all_repos = []
        apps = self.load_all_apps()
        
        for app in apps:
            all_repos.extend(app.repos)
        
        return all_repos
    
    def get_apps_by_stack(self, stack: str) -> List[AppEntry]:
        """
        Get applications filtered by technology stack.
        
        Args:
            stack: Technology stack name (e.g., "Java", "Python").
            
        Returns:
            List of matching AppEntry objects.
        """
        apps = self.load_all_apps()
        return [app for app in apps if app.stack.lower() == stack.lower()]
    
    def get_apps_by_tier(self, tier: str) -> List[AppEntry]:
        """
        Get applications filtered by service tier.
        
        Args:
            tier: Service tier (e.g., "Tier 1", "Tier 2").
            
        Returns:
            List of matching AppEntry objects.
        """
        apps = self.load_all_apps()
        return [app for app in apps if app.tier.lower() == tier.lower()]
