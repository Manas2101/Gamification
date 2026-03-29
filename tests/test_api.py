"""
Test suite for API Module
Tests DataSight and GitHub API clients

Author: DevOps Transformation Team
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.api.datasight import DataSightClient
from src.api.github import GitHubClient


class TestDataSightClient:
    """Test DataSight API client"""
    
    @pytest.fixture
    def client(self):
        """Create DataSight API client"""
        return DataSightClient(bearer_token="test_token_123")
    
    def test_initialization(self, client):
        """Test API client initialization"""
        assert client.bearer_token == "test_token_123"
        assert client.BASE_URL is not None
    
    def test_initialization_no_token(self):
        """Test initialization fails without token"""
        with pytest.raises(ValueError):
            DataSightClient(bearer_token="")
    
    def test_format_date(self, client):
        """Test date formatting"""
        date = datetime(2024, 3, 15)
        result = client._format_date(date)
        assert result == "2024-03"
    
    @patch('src.api.datasight.requests.get')
    def test_get_mttr_success(self, mock_get, client):
        """Test successful MTTR retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {'data': [{'mttr': 2.5}]}
        mock_get.return_value = mock_response
        
        result = client.get_mttr("test_pod", "5", datetime.now(), datetime.now())
        
        assert result == 2.5
        assert mock_get.called
    
    @patch('src.api.datasight.requests.get')
    def test_get_mttr_no_data(self, mock_get, client):
        """Test MTTR with no data returned"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        result = client.get_mttr("test_pod", "5", datetime.now(), datetime.now())
        
        assert result == 0
    
    @patch('src.api.datasight.requests.get')
    def test_get_lttd_success(self, mock_get, client):
        """Test successful LTTD retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {'data': [{'lttd': 1.8}]}
        mock_get.return_value = mock_response
        
        result = client.get_lttd("test_pod", "5", datetime.now(), datetime.now())
        
        assert result == 1.8
    
    @patch('src.api.datasight.requests.get')
    def test_get_release_frequency_success(self, mock_get, client):
        """Test successful RF retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {'data': [{'ytd_pdptppy_basis': 15}]}
        mock_get.return_value = mock_response
        
        result = client.get_release_frequency("test_pod", "5", datetime.now(), datetime.now())
        
        assert result == 15
    
    @patch('src.api.datasight.requests.get')
    def test_get_cfr_success(self, mock_get, client):
        """Test successful CFR retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {'data': [{'change_failure_rate': 5.2}]}
        mock_get.return_value = mock_response
        
        result = client.get_cfr("test_pod", "5", datetime.now(), datetime.now())
        
        assert result == 5.2
    
    @patch('src.api.datasight.requests.get')
    def test_get_all_metrics(self, mock_get, client):
        """Test fetching all metrics"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {'data': [{'mttr': 2.0}]}
        mock_get.return_value = mock_response
        
        result = client.get_all_metrics("test_pod", "5", datetime.now(), datetime.now())
        
        assert 'mttr' in result
        assert 'lttd' in result
        assert 'rf' in result
        assert 'cfr' in result


class TestGitHubClient:
    """Test GitHub API client"""
    
    @pytest.fixture
    def client(self):
        """Create GitHub API client"""
        return GitHubClient(token="test_github_token")
    
    def test_initialization(self, client):
        """Test GitHub client initialization"""
        assert client.token == "test_github_token"
        assert 'Authorization' in client.headers
    
    def test_initialization_no_token(self):
        """Test initialization fails without token"""
        with pytest.raises(ValueError):
            GitHubClient(token="")
    
    def test_analyze_docs_state_with_docs(self, client):
        """Test docs state analysis with docs folder"""
        tree_paths = [
            'README.md',
            'docs/architecture.md',
            'docs/api.md',
            'src/main.py'
        ]
        
        result = client.analyze_docs_state(tree_paths)
        
        assert result['has_readme'] is True
        assert result['has_docs_folder'] is True
        assert len(result['existing_docs']) == 2
    
    def test_analyze_docs_state_no_docs(self, client):
        """Test docs state analysis without docs folder"""
        tree_paths = ['src/main.py', 'src/utils.py']
        
        result = client.analyze_docs_state(tree_paths)
        
        assert result['has_readme'] is False
        assert result['has_docs_folder'] is False
        assert len(result['existing_docs']) == 0
    
    @patch('src.api.github.requests.get')
    def test_get_repository_info_success(self, mock_get, client):
        """Test successful repo info retrieval"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'test-repo',
            'default_branch': 'main'
        }
        mock_get.return_value = mock_response
        
        result = client.get_repository_info("org/test-repo")
        
        assert result is not None
        assert result['name'] == 'test-repo'
    
    @patch('src.api.github.requests.get')
    def test_get_repository_info_not_found(self, mock_get, client):
        """Test repo info when not found"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        result = client.get_repository_info("org/nonexistent")
        
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
