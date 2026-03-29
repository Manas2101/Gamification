"""
Test suite for Core Module
Tests MetricsCalculator, BadgeEngine, and RecommendationEngine

Author: DevOps Transformation Team
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.core.calculator import MetricsCalculator
from src.core.badges import BadgeEngine, compute_badges, get_badge_tier
from src.core.recommendations import RecommendationEngine


class TestMetricsCalculator:
    """Test MetricsCalculator scoring logic"""
    
    @pytest.fixture
    def calculator(self):
        """Create MetricsCalculator instance"""
        return MetricsCalculator()
    
    def test_initialization(self, calculator):
        """Test calculator initialization"""
        assert calculator is not None
        assert sum(calculator.WEIGHTS.values()) == pytest.approx(1.0)
    
    def test_calculate_release_velocity_perfect(self, calculator):
        """Test Release Velocity with perfect metrics"""
        metrics = {
            'rf': 25,
            'lttd': 0.5,
            'ci': True,
            'cd': True,
            'zero_touch_deployment': True
        }
        
        score = calculator.calculate_release_velocity(metrics)
        
        assert score >= 90
        assert score <= 100
    
    def test_calculate_release_velocity_poor(self, calculator):
        """Test Release Velocity with poor metrics"""
        metrics = {
            'rf': 1,
            'lttd': 10,
            'ci': False,
            'cd': False
        }
        
        score = calculator.calculate_release_velocity(metrics)
        
        assert score < 50
    
    def test_calculate_git_hygiene(self, calculator):
        """Test Git Hygiene score passthrough"""
        metrics = {'git_hygiene_score': 85.0}
        
        score = calculator.calculate_git_hygiene(metrics)
        
        assert score == 85.0
    
    def test_calculate_git_hygiene_missing(self, calculator):
        """Test Git Hygiene with missing score"""
        metrics = {}
        
        score = calculator.calculate_git_hygiene(metrics)
        
        assert score == 50.0  # Default
    
    def test_calculate_pipeline_maturity_perfect(self, calculator):
        """Test Pipeline Maturity with all features"""
        metrics = {
            'ci': True,
            'cd': True,
            'rollback': True,
            'self_service': True,
            'pipeline_standard': True
        }
        
        score = calculator.calculate_pipeline_maturity(metrics)
        
        assert score == 100.0
    
    def test_calculate_pipeline_maturity_partial(self, calculator):
        """Test Pipeline Maturity with some features"""
        metrics = {
            'ci': True,
            'cd': True,
            'rollback': False,
            'self_service': False,
            'pipeline_standard': False
        }
        
        score = calculator.calculate_pipeline_maturity(metrics)
        
        assert score == 40.0
    
    def test_calculate_compliance_perfect(self, calculator):
        """Test Compliance with all requirements"""
        metrics = {
            'release_page_url': 'https://example.com',
            'compliance_evidence_page': 'https://example.com',
            'is_priv_access_current': True,
            'cr_auto_creation': True
        }
        
        score = calculator.calculate_compliance(metrics)
        
        assert score == 100.0
    
    def test_calculate_quality_security_perfect(self, calculator):
        """Test Quality & Security with all features"""
        metrics = {
            'sast_enabled': True,
            'sonarqube_project': 'project-key',
            'data_classification': 'Confidential'
        }
        
        score = calculator.calculate_quality_security(metrics)
        
        assert score == 100.0
    
    def test_calculate_adoption_perfect(self, calculator):
        """Test Adoption with all features"""
        metrics = {
            'copilot_enabled': True,
            'ai_tools_declared': True,
            'apis_published': 3,
            'feature_flags_adopted': True
        }
        
        score = calculator.calculate_adoption(metrics)
        
        assert score == 100.0
    
    def test_calculate_all_scores(self, calculator):
        """Test complete scoring calculation"""
        metrics = {
            'rf': 15, 'lttd': 1.0, 'ci': True, 'cd': True,
            'git_hygiene_score': 85.0,
            'rollback': True, 'self_service': True, 'pipeline_standard': True,
            'release_page_url': 'url', 'compliance_evidence_page': 'url',
            'is_priv_access_current': True, 'cr_auto_creation': True,
            'sast_enabled': True, 'sonarqube_project': 'proj',
            'data_classification': 'Confidential',
            'copilot_enabled': True, 'ai_tools_declared': True,
            'apis_published': 2, 'feature_flags_adopted': True
        }
        
        result = calculator.calculate_all_scores(metrics)
        
        assert 'Release_Velocity_Score' in result
        assert 'Git_Hygiene_Score' in result
        assert 'Pipeline_Maturity_Score' in result
        assert 'Compliance_Score' in result
        assert 'Quality_Security_Score' in result
        assert 'Adoption_Score' in result
        assert 'dpi' in result
        
        # All scores should be 0-100
        for key, value in result.items():
            assert 0 <= value <= 100, f"{key} out of range: {value}"
    
    def test_dpi_weighted_calculation(self, calculator):
        """Test DPI is correctly weighted"""
        scores = {
            'Release_Velocity_Score': 80,
            'Git_Hygiene_Score': 80,
            'Pipeline_Maturity_Score': 80,
            'Compliance_Score': 80,
            'Quality_Security_Score': 80,
            'Adoption_Score': 80
        }
        
        dpi = calculator.calculate_dpi(
            scores['Release_Velocity_Score'],
            scores['Git_Hygiene_Score'],
            scores['Pipeline_Maturity_Score'],
            scores['Compliance_Score'],
            scores['Quality_Security_Score'],
            scores['Adoption_Score']
        )
        
        assert dpi == 80.0  # All equal, so weighted average = 80


class TestBadgeEngine:
    """Test BadgeEngine badge computation"""
    
    @pytest.fixture
    def engine(self):
        """Create BadgeEngine instance"""
        return BadgeEngine()
    
    def test_get_tier_platinum(self, engine):
        """Test platinum tier detection"""
        assert engine.get_tier(95) == 'platinum'
        assert engine.get_tier(100) == 'platinum'
    
    def test_get_tier_gold(self, engine):
        """Test gold tier detection"""
        assert engine.get_tier(85) == 'gold'
        assert engine.get_tier(94) == 'gold'
    
    def test_get_tier_silver(self, engine):
        """Test silver tier detection"""
        assert engine.get_tier(70) == 'silver'
        assert engine.get_tier(84) == 'silver'
    
    def test_get_tier_bronze(self, engine):
        """Test bronze tier detection"""
        assert engine.get_tier(50) == 'bronze'
        assert engine.get_tier(69) == 'bronze'
    
    def test_get_tier_none(self, engine):
        """Test no tier for low scores"""
        assert engine.get_tier(49) is None
        assert engine.get_tier(0) is None
    
    def test_compute_dpi_badge_platinum(self, engine):
        """Test DPI badge for platinum score"""
        badge = engine.compute_dpi_badge(96)
        
        assert badge is not None
        assert badge['tier'] == 'Platinum'
        assert 'Elite' in badge['name']
    
    def test_compute_dpi_badge_gold(self, engine):
        """Test DPI badge for gold score"""
        badge = engine.compute_dpi_badge(88)
        
        assert badge is not None
        assert badge['tier'] == 'Gold'
    
    def test_compute_pillar_badges(self, engine):
        """Test pillar badge computation"""
        scores = {
            'Release_Velocity_Score': 90,  # Gold
            'Git_Hygiene_Score': 60,       # No badge
            'Pipeline_Maturity_Score': 95  # Platinum
        }
        
        badges = engine.compute_pillar_badges(scores)
        
        assert len(badges) == 2  # Only gold+ get badges
    
    def test_compute_badges_complete(self, engine):
        """Test complete badge computation"""
        scores = {
            'dpi': 88,
            'Release_Velocity_Score': 90,
            'Git_Hygiene_Score': 85,
            'Pipeline_Maturity_Score': 88,
            'Compliance_Score': 75,
            'Quality_Security_Score': 80,
            'Adoption_Score': 70
        }
        
        badges = engine.compute_badges(scores)
        
        assert len(badges) > 0
        assert any(b.get('tier') == 'Gold' for b in badges)
    
    def test_compute_badges_helper_function(self):
        """Test convenience function"""
        row = {'dpi': 90, 'Release_Velocity_Score': 85}
        
        badges = compute_badges(row)
        
        assert isinstance(badges, list)
    
    def test_get_badge_tier_helper(self):
        """Test tier helper function"""
        assert get_badge_tier(95) == 'Platinum'
        assert get_badge_tier(85) == 'Gold'
        assert get_badge_tier(40) is None


class TestRecommendationEngine:
    """Test RecommendationEngine recommendation generation"""
    
    @pytest.fixture
    def engine(self):
        """Create RecommendationEngine instance"""
        return RecommendationEngine()
    
    def test_generate_recommendations_low_scores(self, engine):
        """Test recommendations for low scores"""
        scores = {
            'Release_Velocity_Score': 40,
            'Git_Hygiene_Score': 45,
            'Pipeline_Maturity_Score': 30,
            'Compliance_Score': 50,
            'Quality_Security_Score': 35,
            'Adoption_Score': 25
        }
        
        recs = engine.generate_recommendations(scores)
        
        assert len(recs) > 0
        assert all('title' in r for r in recs)
        assert all('priority' in r for r in recs)
    
    def test_generate_recommendations_high_scores(self, engine):
        """Test recommendations for high scores"""
        scores = {
            'Release_Velocity_Score': 95,
            'Git_Hygiene_Score': 92,
            'Pipeline_Maturity_Score': 90,
            'Compliance_Score': 95,
            'Quality_Security_Score': 88,
            'Adoption_Score': 90
        }
        
        recs = engine.generate_recommendations(scores)
        
        # Should have few or no recommendations
        assert len(recs) <= 2
    
    def test_recommendations_sorted_by_priority(self, engine):
        """Test recommendations are sorted by priority"""
        scores = {
            'Release_Velocity_Score': 30,
            'Git_Hygiene_Score': 60,
            'Pipeline_Maturity_Score': 20
        }
        
        recs = engine.generate_recommendations(scores)
        
        if len(recs) >= 2:
            priorities = [r['priority'] for r in recs]
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            priority_values = [priority_order.get(p, 3) for p in priorities]
            assert priority_values == sorted(priority_values)
    
    def test_get_quick_wins(self, engine):
        """Test quick wins identification"""
        scores = {
            'Release_Velocity_Score': 60,
            'Git_Hygiene_Score': 40,
            'Pipeline_Maturity_Score': 50
        }
        
        quick_wins = engine.get_quick_wins(scores)
        
        assert isinstance(quick_wins, list)
        for qw in quick_wins:
            assert qw.get('impact') == 'High'
            assert qw.get('effort') == 'Low'
    
    def test_format_recommendations(self, engine):
        """Test recommendation formatting"""
        scores = {'Release_Velocity_Score': 40}
        recs = engine.generate_recommendations(scores)
        
        formatted = engine.format_recommendations(recs)
        
        assert isinstance(formatted, str)
        if recs:
            assert '###' in formatted  # Has headers


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
