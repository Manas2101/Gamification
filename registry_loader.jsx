"""
Registry loader for YAML-based app configuration
Reads app metadata from apps/*.yaml files
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import yaml

logger = logging.getLogger(__name__)

@dataclass
class RepoConfig:
    """Repository configuration"""
    git_org: str
    repo_name: str
    role: str = "backend"
    is_primary: bool = False
    original_url: str = ""  # Store the original Git URL for direct API calls
    
    @property
    def full_name(self) -> str:
        return f"{self.git_org}/{self.repo_name}"
    
    @property
    def api_base_url(self) -> str:
        """
        Convert Git URL to API base URL
        
        Examples:
            "https://alm-github.systems.uk.hsbc/GCDU-Repository/repo.git"
            -> "https://alm-github.systems.uk.hsbc/api/v3/repos/GCDU-Repository/repo"
            
            "https://github.com/myorg/repo.git"
            -> "https://api.github.com/repos/myorg/repo"
        """
        if not self.original_url:
            # Fallback to constructed URL if no original_url
            if 'hsbc' in self.git_org.lower() or 'alm-github' in self.git_org.lower():
                return f"https://alm-github.systems.uk.hsbc/api/v3/repos/{self.git_org}/{self.repo_name}"
            else:
                return f"https://api.github.com/repos/{self.git_org}/{self.repo_name}"
        
        # Parse original URL to build API URL
        url = self.original_url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # Detect GitHub instance type
        if 'alm-github.systems.uk.hsbc' in url:
            # Internal GitHub Enterprise
            # Extract org and repo from URL path
            parts = url.split('/')
            if len(parts) >= 2:
                org = parts[-2]
                repo = parts[-1]
                return f"https://alm-github.systems.uk.hsbc/api/v3/repos/{org}/{repo}"
        elif 'github.com' in url:
            # Public GitHub
            parts = url.split('/')
            if len(parts) >= 2:
                org = parts[-2]
                repo = parts[-1]
                return f"https://api.github.com/repos/{org}/{repo}"
        
        # Fallback
        return f"https://api.github.com/repos/{self.git_org}/{self.repo_name}"

@dataclass
class AppEntry:
    """Complete app registry entry"""
    app_id: str  # This will be the EIM ID
    app_name: str
    eim: str = ""
    teambook_pods: List[str] = field(default_factory=list)
    teambook_level: str = "4"
    
    # Team
    itso: str = ""
    team_lead_email: str = ""
    release_champion: List[str] = field(default_factory=list)
    
    # Classification
    app_type: str = "traditional"
    stack: str = "java-spring"
    in_production: bool = True
    tier: int = 2
    
    # Repositories
    repos: List[RepoConfig] = field(default_factory=list)
    
    # Pipeline flags
    ci_automated: bool = False
    cd_automated: bool = False
    standard_pipeline_adopted: bool = False
    pipeline_standard: str = "v1"  # "v1" or "v2"
    git_hygiene_adopted: bool = False
    cr_auto_creation: bool = False
    zero_touch_deployment: bool = False
    automated_rollback: bool = False
    feature_flags_adopted: bool = False
    approval_gate_count: int = 0
    
    # Access & Security
    priv_access_for_deploy: bool = True
    priv_access_reviewed_date: Optional[str] = None
    sast_enabled: bool = False
    data_classification: str = "internal"
    
    # Compliance
    release_page_url: str = ""
    compliance_evidence_page: str = ""
    
    # AI & Adoption
    copilot_enabled: bool = False
    ai_tools_declared: List[str] = field(default_factory=list)
    ai_test_generation: bool = False
    apis_published: bool = False
    catalog_url: str = ""
    api_count: int = 0
    
    # Quality & Security
    sonarqube_project: str = ""
    
    # Interview notes
    improvement_action_1: str = ""
    improvement_action_2: str = ""
    improvement_action_3: str = ""
    notes: str = ""
    
    @property
    def primary_repo(self) -> Optional[RepoConfig]:
        """Get the primary repository"""
        for repo in self.repos:
            if repo.is_primary:
                return repo
        return self.repos[0] if self.repos else None
    
    @property
    def has_release_page(self) -> bool:
        return bool(self.release_page_url and self.release_page_url.strip())
    
    @property
    def has_compliance_evidence(self) -> bool:
        return bool(self.compliance_evidence_page and self.compliance_evidence_page.strip())
    
    @property
    def is_priv_access_current(self) -> bool:
        """Check if privileged access review is within 90 days"""
        if not self.priv_access_reviewed_date:
            return False
        try:
            reviewed = datetime.strptime(self.priv_access_reviewed_date, "%Y-%m-%d")
            return (datetime.now() - reviewed) <= timedelta(days=90)
        except ValueError:
            return False
    
    @property
    def display_name(self) -> str:
        return self.app_name
    
    @property
    def service_line(self) -> str:
        return "Default Service Line"  # Can be added to YAML if needed


class RegistryLoader:
    """Loads app configurations from YAML registry"""
    
    def __init__(self, registry_dir: str = None):
        """Initialize registry loader"""
        if registry_dir is None:
            # Default to apps/ directory relative to this file
            registry_dir = Path(__file__).parent / "apps"
        self.registry_dir = Path(registry_dir)
        
        if not self.registry_dir.exists():
            logger.warning(f"Registry directory not found: {self.registry_dir}")
            self.registry_dir.mkdir(parents=True, exist_ok=True)
    
    def _extract_repo_name_from_url(self, url: str) -> str:
        """
        Extract repository name from Git URL
        
        Examples:
            "https://alm-github.systems.uk.hsbc/GCDU-Repository/gdt-mds-gcdu-101-acct-srch-pa.git"
            -> "gdt-mds-gcdu-101-acct-srch-pa"
            
            "https://github.com/myorg/my-repo.git"
            -> "my-repo"
        """
        if not url:
            return ""
        
        # Remove .git extension if present
        url = url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # Extract last part of path (repo name)
        parts = url.split('/')
        if len(parts) >= 2:
            return parts[-1]
        
        return ""
    
    def _extract_git_org_from_url(self, url: str) -> str:
        """
        Extract git organization from Git URL
        
        Examples:
            "https://alm-github.systems.uk.hsbc/GCDU-Repository/gdt-mds-gcdu-101-acct-srch-pa.git"
            -> "GCDU-Repository"
            
            "https://github.com/myorg/my-repo.git"
            -> "myorg"
        """
        if not url:
            return ""
        
        # Remove .git extension if present
        url = url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # Extract second-to-last part of path (org name)
        parts = url.split('/')
        if len(parts) >= 2:
            return parts[-2]
        
        return ""
    
    def load_all(self) -> List[AppEntry]:
        """Load all app entries from registry"""
        apps = []
        
        if not self.registry_dir.exists():
            logger.warning(f"Registry directory does not exist: {self.registry_dir}")
            return apps
        
        for yaml_file in self.registry_dir.glob("*.yaml"):
            try:
                app = self.load_app(yaml_file)
                if app:
                    apps.append(app)
            except Exception as e:
                logger.error(f"Error loading {yaml_file}: {e}")
        
        logger.info(f"Loaded {len(apps)} apps from registry")
        return apps
    
    def load_app(self, yaml_path: Path) -> Optional[AppEntry]:
        """Load a single app from YAML file"""
        try:
            # Try UTF-8 first, then fallback to cp1252 (Windows encoding)
            data = None
            for encoding in ['utf-8', 'cp1252', 'latin-1']:
                try:
                    with open(yaml_path, encoding=encoding) as f:
                        data = yaml.safe_load(f)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if data is None:
                logger.error(f"Error parsing {yaml_path}: Could not decode file with any supported encoding")
                return None
            
            if not data:
                return None
            
            # Extract EIM from filename (e.g., 9594666.yaml -> 9594666)
            eim_id = yaml_path.stem
            
            # Parse repositories - support multiple formats
            repos = []
            repos_data = data.get("repos", [])
            
            for idx, repo_data in enumerate(repos_data):
                if isinstance(repo_data, dict):
                    # Format 1: Dict with git_org and repo_name fields
                    if "git_org" in repo_data and "repo_name" in repo_data:
                        repo_name = repo_data.get("repo_name", "")
                        # Handle both string and list format for repo_name
                        if isinstance(repo_name, list):
                            repo_name = repo_name[0] if repo_name else ""
                        
                        repos.append(RepoConfig(
                            git_org=repo_data.get("git_org", ""),
                            repo_name=str(repo_name),
                            role=repo_data.get("role", "backend"),
                            is_primary=repo_data.get("is_primary", False)
                        ))
                    
                    # Format 2: Dict with git_org and list of URLs
                    elif "git_org" in repo_data and "repos" in repo_data:
                        git_org_name = repo_data.get("git_org", "")
                        repo_urls = repo_data.get("repos", [])
                        
                        for url_idx, repo_url in enumerate(repo_urls):
                            # Extract repo name from URL
                            # e.g., "https://alm-github.systems.uk.hsbc/GCDU-Repository/gdt-mds-gcdu-101-acct-srch-pa.git"
                            # -> git_org: "GCDU-Repository", repo_name: "gdt-mds-gcdu-101-acct-srch-pa"
                            repo_name = self._extract_repo_name_from_url(repo_url)
                            actual_git_org = self._extract_git_org_from_url(repo_url)
                            
                            if repo_name:
                                repos.append(RepoConfig(
                                    git_org=actual_git_org or git_org_name,
                                    repo_name=repo_name,
                                    role="backend",
                                    is_primary=(idx == 0 and url_idx == 0),  # First repo is primary
                                    original_url=repo_url  # Store original URL for direct API usage
                                ))
                
                elif isinstance(repo_data, str):
                    # Format 3: Direct URL string
                    repo_name = self._extract_repo_name_from_url(repo_data)
                    git_org = self._extract_git_org_from_url(repo_data)
                    
                    if repo_name:
                        repos.append(RepoConfig(
                            git_org=git_org or "unknown",
                            repo_name=repo_name,
                            role="backend",
                            is_primary=(idx == 0),
                            original_url=repo_data  # Store original URL for direct API usage
                        ))
            
            # Parse release champion (can be string or list)
            release_champion = data.get("release_champion", [])
            if isinstance(release_champion, str):
                # Handle malformed string like "["name1","name2"]"
                if release_champion.startswith('["') and release_champion.endswith('"]'):
                    import json
                    try:
                        release_champion = json.loads(release_champion)
                    except:
                        release_champion = [release_champion]
                else:
                    release_champion = [release_champion]
            
            # Parse teambook pods (new field name)
            teambook_pods = data.get("teambook_pods", [])
            if not teambook_pods:
                # Fallback to old field names for backward compatibility
                teambook_pods = data.get("datasigh_pods", [])
            if not teambook_pods:
                teambook_pods = data.get("datasight_pods", [])
            
            app = AppEntry(
                app_id=eim_id,
                app_name=data.get("app_name", eim_id),
                eim=data.get("eim", eim_id),
                teambook_pods=teambook_pods,
                teambook_level=str(data.get("teambook_level", "4")),
                
                itso=data.get("itso", ""),
                team_lead_email=data.get("team_lead_email", ""),
                release_champion=release_champion,
                
                app_type=data.get("app_type", "traditional"),
                stack=data.get("stack", "java-spring"),
                in_production=data.get("in_production", True),
                tier=int(data.get("tier", 2)),
                
                repos=repos,
                
                ci_automated=data.get("ci_automated", False),
                cd_automated=data.get("cd_automated", False),
                standard_pipeline_adopted=data.get("standard_pipeline_adopted", False),
                git_hygiene_adopted=data.get("git_hygiene_adopted", False),
                cr_auto_creation=data.get("cr_auto_creation", False),
                zero_touch_deployment=data.get("zero_touch_deployment", False),
                automated_rollback=data.get("automated_rollback", False),
                feature_flags_adopted=data.get("feature_flags_adopted", False),
                approval_gate_count=int(data.get("approval_gate_count", 0)),
                
                priv_access_for_deploy=data.get("priv_access_for_deploy", True),
                priv_access_reviewed_date=data.get("priv_access_reviewed_date", ""),
                sast_enabled=data.get("sast_enabled", False),
                data_classification=data.get("data_classification", "internal"),
                
                release_page_url=data.get("release_page_url", ""),
                compliance_evidence_page=data.get("compliance_evidence_page", ""),
                
                copilot_enabled=data.get("copilot_enabled", False),
                ai_tools_declared=data.get("ai_tools_declared", []),
                ai_test_generation=data.get("ai_test_generation", False),
                apis_published=data.get("apis_published", False),
                catalog_url=data.get("catalog_url", ""),
                api_count=int(data.get("api_count", 0)),
                
                improvement_action_1=data.get("improvement_action_1", ""),
                improvement_action_2=data.get("improvement_action_2", ""),
                improvement_action_3=data.get("improvement_action_3", ""),
                notes=data.get("notes", ""),
            )
            
            return app
            
        except Exception as e:
            logger.error(f"Error parsing {yaml_path}: {e}")
            return None
    
    def get_app(self, app_id: str) -> Optional[AppEntry]:
        """Load a specific app by ID"""
        yaml_path = self.registry_dir / f"{app_id}.yaml"
        if yaml_path.exists():
            return self.load_app(yaml_path)
        return None
    
    def get_apps_by_pod(self, pod_name: str) -> List[AppEntry]:
        """Find all apps that contain a specific DataSight pod"""
        apps = self.load_all()
        return [app for app in apps if pod_name in app.datasight_pods]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    loader = RegistryLoader()
    apps = loader.load_all()
    
    print(f"\nLoaded {len(apps)} apps:")
    for app in apps:
        print(f"  - EIM {app.eim}: {app.app_name}")
        print(f"    TeamBook Pods: {app.teambook_pods} (Level: {app.teambook_level})")
        print(f"    Type: {app.app_type}, Tier: {app.tier}")
        print(f"    CI: {app.ci_automated}, CD: {app.cd_automated}")
