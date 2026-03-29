"""
Test suite for Data Module
Tests Database and RegistryLoader

Author: DevOps Transformation Team
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import tempfile
from datetime import datetime

from src.data.database import Database
from src.data.registry import RegistryLoader, AppEntry, RepoInfo


class TestDatabase:
    """Test Database operations"""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create temporary database"""
        db_path = tmp_path / "test_metrics.db"
        return Database(str(db_path))
    
    def test_initialization(self, db):
        """Test database initialization"""
        assert db is not None
        assert os.path.exists(db.db_path)
    
    def test_upsert_pod(self, db):
        """Test pod insertion"""
        db.upsert_pod(
            pod_id="123",
            pod_name="test_pod",
            stack="Java",
            business_unit="BU1",
            tier="Tier 1"
        )
        
        pods = db.get_all_pods()
        assert len(pods) == 1
        assert pods.iloc[0]['pod_name'] == "test_pod"
    
    def test_upsert_pod_update(self, db):
        """Test pod update"""
        db.upsert_pod("123", "test_pod", "Java", "BU1", "Tier 1")
        db.upsert_pod("123", "updated_pod", "Python", "BU2", "Tier 2")
        
        pods = db.get_all_pods()
        assert len(pods) == 1
        assert pods.iloc[0]['pod_name'] == "updated_pod"
        assert pods.iloc[0]['stack'] == "Python"
    
    def test_insert_weekly_metrics(self, db):
        """Test weekly metrics insertion"""
        db.upsert_pod("123", "test_pod", "Java", "BU1", "Tier 1")
        
        metrics = {
            'pod_id': '123',
            'week_date': datetime.now(),
            'mttr': 2.5,
            'lttd': 1.8,
            'rf': 10,
            'cfr': 5.0,
            'git_hygiene_score': 85.0,
            'Release_Velocity_Score': 80,
            'Git_Hygiene_Score': 85,
            'Pipeline_Maturity_Score': 75,
            'Compliance_Score': 70,
            'Quality_Security_Score': 80,
            'Adoption_Score': 65,
            'dpi': 76
        }
        
        db.insert_weekly_metrics(metrics)
        
        latest = db.get_latest_metrics()
        assert len(latest) == 1
        assert latest.iloc[0]['dpi'] == 76
    
    def test_get_pod_history(self, db):
        """Test historical metrics retrieval"""
        db.upsert_pod("123", "test_pod", "Java", "BU1", "Tier 1")
        
        # Insert multiple weeks
        for i in range(3):
            metrics = {
                'pod_id': '123',
                'week_date': f'2024-03-{10+i*7:02d}',
                'dpi': 70 + i * 5
            }
            db.insert_weekly_metrics(metrics)
        
        history = db.get_pod_history("123", weeks=3)
        assert len(history) == 3
    
    def test_get_leaderboard(self, db):
        """Test leaderboard retrieval"""
        # Insert multiple pods
        for i in range(3):
            db.upsert_pod(f"pod_{i}", f"Team {i}", "Java", "BU1", "Tier 1")
            db.insert_weekly_metrics({
                'pod_id': f'pod_{i}',
                'week_date': '2024-03-25',
                'dpi': 60 + i * 10
            })
        
        leaderboard = db.get_leaderboard()
        assert len(leaderboard) == 3
        # Should be sorted by DPI descending
        assert leaderboard.iloc[0]['dpi'] >= leaderboard.iloc[1]['dpi']
    
    def test_get_statistics(self, db):
        """Test statistics retrieval"""
        db.upsert_pod("123", "test_pod", "Java", "BU1", "Tier 1")
        db.insert_weekly_metrics({
            'pod_id': '123',
            'week_date': '2024-03-25',
            'dpi': 75
        })
        
        stats = db.get_statistics()
        
        assert stats['total_pods'] == 1
        assert stats['total_metrics_records'] == 1
        assert stats['average_dpi'] == 75
    
    def test_delete_pod(self, db):
        """Test pod deletion"""
        db.upsert_pod("123", "test_pod", "Java", "BU1", "Tier 1")
        db.insert_weekly_metrics({
            'pod_id': '123',
            'week_date': '2024-03-25',
            'dpi': 75
        })
        
        db.delete_pod("123")
        
        pods = db.get_all_pods()
        assert len(pods) == 0


class TestRegistryLoader:
    """Test RegistryLoader YAML parsing"""
    
    @pytest.fixture
    def temp_registry(self, tmp_path):
        """Create temporary registry directory with test YAML"""
        registry_dir = tmp_path / "apps"
        registry_dir.mkdir()
        
        # Create test YAML file
        yaml_content = """
app_id: "12345"
app_name: "Test Application"
pod_name: "test-pod"
pod_level: "5"
stack: "Java"
tier: "Tier 1"
business_unit: "Engineering"
repos:
  - git_org: "myorg"
    repo_name: "myrepo"
  - git_org: "myorg"
    repo_name: "myrepo2"
ci: true
cd: true
sast_enabled: true
copilot_enabled: false
"""
        yaml_file = registry_dir / "12345.yaml"
        yaml_file.write_text(yaml_content)
        
        return str(registry_dir)
    
    def test_load_all_apps(self, temp_registry):
        """Test loading all apps from registry"""
        loader = RegistryLoader(temp_registry)
        apps = loader.load_all_apps()
        
        assert len(apps) == 1
        assert apps[0].app_name == "Test Application"
    
    def test_load_app_details(self, temp_registry):
        """Test app details are loaded correctly"""
        loader = RegistryLoader(temp_registry)
        apps = loader.load_all_apps()
        app = apps[0]
        
        assert app.app_id == "12345"
        assert app.pod_name == "test-pod"
        assert app.stack == "Java"
        assert app.tier == "Tier 1"
        assert len(app.repos) == 2
    
    def test_repo_info(self, temp_registry):
        """Test repository info parsing"""
        loader = RegistryLoader(temp_registry)
        apps = loader.load_all_apps()
        repo = apps[0].repos[0]
        
        assert repo.git_org == "myorg"
        assert repo.repo_name == "myrepo"
        assert repo.full_name == "myorg/myrepo"
    
    def test_config_flags(self, temp_registry):
        """Test configuration flags parsing"""
        loader = RegistryLoader(temp_registry)
        apps = loader.load_all_apps()
        config = apps[0].config
        
        assert config['ci'] is True
        assert config['cd'] is True
        assert config['sast_enabled'] is True
        assert config['copilot_enabled'] is False
    
    def test_get_app_by_id(self, temp_registry):
        """Test getting specific app by ID"""
        loader = RegistryLoader(temp_registry)
        app = loader.get_app_by_id("12345")
        
        assert app is not None
        assert app.app_name == "Test Application"
    
    def test_get_app_by_id_not_found(self, temp_registry):
        """Test getting non-existent app"""
        loader = RegistryLoader(temp_registry)
        app = loader.get_app_by_id("99999")
        
        assert app is None
    
    def test_get_all_repos(self, temp_registry):
        """Test getting all repos from registry"""
        loader = RegistryLoader(temp_registry)
        repos = loader.get_all_repos()
        
        assert len(repos) == 2
        assert all(isinstance(r, RepoInfo) for r in repos)
    
    def test_empty_registry(self, tmp_path):
        """Test loading from empty registry"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        loader = RegistryLoader(str(empty_dir))
        apps = loader.load_all_apps()
        
        assert len(apps) == 0
    
    def test_nonexistent_registry(self, tmp_path):
        """Test loading from non-existent directory"""
        loader = RegistryLoader(str(tmp_path / "nonexistent"))
        apps = loader.load_all_apps()
        
        assert len(apps) == 0


class TestRepoInfo:
    """Test RepoInfo dataclass"""
    
    def test_full_name(self):
        """Test full_name property"""
        repo = RepoInfo(git_org="myorg", repo_name="myrepo")
        
        assert repo.full_name == "myorg/myrepo"


class TestAppEntry:
    """Test AppEntry dataclass"""
    
    def test_default_values(self):
        """Test default values"""
        app = AppEntry(app_id="123", app_name="Test")
        
        assert app.pod_level == "5"
        assert app.repos == []
        assert app.config == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
