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
        """Test Compliance with all requirements (5 components @ 20 pts each)"""
        metrics = {
            'release_page_url': 'https://example.com',
            'compliance_evidence_page': 'https://example.com',
            'repo_docs': 'https://docs.example.com',
            'is_priv_access_current': True,
            'cr_auto_creation': True
        }
        
        score = calculator.calculate_compliance(metrics)
        
        assert score == 100.0
    
    def test_calculate_compliance_partial(self, calculator):
        """Test Compliance with partial requirements"""
        metrics = {
            'release_page_url': 'https://example.com',
            'compliance_evidence_page': '',
            'repo_docs': 'https://docs.example.com',
            'is_priv_access_current': False,
            'cr_auto_creation': True
        }
        
        score = calculator.calculate_compliance(metrics)
        
        assert score == 60.0  # 3 out of 5 = 60 points
    
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
        """Test Adoption with all features (boolean IADP/APIX)"""
        metrics = {
            'copilot_enabled': True,
            'ai_tools_declared': True,
            'apis_published_iadp': True,
            'apis_published_apix': True,
            'ai_devops_onboarded': True
        }
        
        score = calculator.calculate_adoption(metrics)
        
        assert score == 100.0  # 30 + 10 + 20 + 20 + 20 = 100
    
    def test_calculate_adoption_partial(self, calculator):
        """Test Adoption with partial features"""
        metrics = {
            'copilot_enabled': True,
            'ai_tools_declared': False,
            'apis_published_iadp': True,
            'apis_published_apix': False,
            'ai_devops_onboarded': False
        }
        
        score = calculator.calculate_adoption(metrics)
        
        assert score == 50.0  # 30 + 0 + 20 + 0 + 0 = 50
    
    def test_calculate_adoption_only_apis(self, calculator):
        """Test Adoption with only API flags"""
        metrics = {
            'copilot_enabled': False,
            'ai_tools_declared': False,
            'apis_published_iadp': True,
            'apis_published_apix': True,
            'ai_devops_onboarded': False
        }
        
        score = calculator.calculate_adoption(metrics)
        
        assert score == 40.0  # 0 + 0 + 20 + 20 + 0 = 40
    
    def test_calculate_all_scores(self, calculator):
        """Test complete scoring calculation with new fields"""
        metrics = {
            'rf': 15, 'lttd': 1.0, 'ci': True, 'cd': True,
            'git_hygiene_score': 85.0,
            'rollback': True, 'zero_touch_deployment': True, 'pipeline_standard': True,
            'release_page_url': 'url', 'compliance_evidence_page': 'url',
            'repo_docs': 'https://docs.example.com',
            'is_priv_access_current': True, 'cr_auto_creation': True,
            'sast_enabled': True, 'sonarqube_project': 'proj',
            'data_classification': 'Confidential',
            'copilot_enabled': True, 'ai_tools_declared': True,
            'apis_published_iadp': True, 'apis_published_apix': True,
            'ai_devops_onboarded': True
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
    
    def test_sample_scoring_team_a_excellent(self, calculator):
        """
        Sample Scoring: Team A - Excellent Performance
        
        Team Profile:
        - High deployment frequency (280/year)
        - Fast lead time (1.8 days)
        - Full CI/CD automation
        - Strong hygiene (95/100)
        - All compliance requirements met
        - Full adoption of modern practices
        """
        metrics = {
            # Release Velocity
            'rf': 280, 'lttd': 1.8,
            # Pipeline Maturity
            'ci': True, 'cd': True, 'rollback': True,
            'zero_touch_deployment': True, 'pipeline_standard': True,
            # Git Hygiene
            'git_hygiene_score': 95.0,
            # Compliance
            'release_page_url': 'https://releases.example.com',
            'compliance_evidence_page': 'https://compliance.example.com',
            'repo_docs': 'https://docs.example.com',
            'is_priv_access_current': True,
            'cr_auto_creation': True,
            # Quality & Security
            'sast_enabled': True,
            'sonarqube_project': 'team-a-project',
            'data_classification': 'Confidential',
            # Adoption
            'copilot_enabled': True,
            'ai_tools_declared': True,
            'apis_published_iadp': True,
            'apis_published_apix': True,
            'ai_devops_onboarded': True
        }
        
        result = calculator.calculate_all_scores(metrics)
        
        # Expected scores
        assert result['Release_Velocity_Score'] == 100.0  # RF=280 (100) + LTTD=1.8 (100)
        assert result['Git_Hygiene_Score'] == 95.0
        assert result['Pipeline_Maturity_Score'] == 100.0  # All 5 components
        assert result['Compliance_Score'] == 100.0  # All 5 components
        assert result['Quality_Security_Score'] == 100.0  # All 3 components
        assert result['Adoption_Score'] == 100.0  # All 5 components
        assert result['dpi'] >= 98.0  # Weighted average should be ~99
    
    def test_sample_scoring_team_b_good(self, calculator):
        """
        Sample Scoring: Team B - Good Performance
        
        Team Profile:
        - Moderate deployment frequency (140/year)
        - Acceptable lead time (5 days)
        - Partial automation
        - Good hygiene (75/100)
        - Some compliance gaps
        - Partial adoption
        """
        metrics = {
            # Release Velocity
            'rf': 140, 'lttd': 5.0,
            # Pipeline Maturity
            'ci': True, 'cd': True, 'rollback': False,
            'zero_touch_deployment': False, 'pipeline_standard': True,
            # Git Hygiene
            'git_hygiene_score': 75.0,
            # Compliance
            'release_page_url': 'https://releases.example.com',
            'compliance_evidence_page': '',
            'repo_docs': 'https://docs.example.com',
            'is_priv_access_current': True,
            'cr_auto_creation': False,
            # Quality & Security
            'sast_enabled': True,
            'sonarqube_project': 'team-b-project',
            'data_classification': 'Internal',
            # Adoption
            'copilot_enabled': True,
            'ai_tools_declared': False,
            'apis_published_iadp': True,
            'apis_published_apix': False,
            'ai_devops_onboarded': False
        }
        
        result = calculator.calculate_all_scores(metrics)
        
        # Expected scores
        assert result['Release_Velocity_Score'] == pytest.approx(75.0, abs=5)  # RF=140 (70) + LTTD=5 (80)
        assert result['Git_Hygiene_Score'] == 75.0
        assert result['Pipeline_Maturity_Score'] == 60.0  # 3 out of 5
        assert result['Compliance_Score'] == 60.0  # 3 out of 5
        assert result['Quality_Security_Score'] == 100.0  # All 3 components
        assert result['Adoption_Score'] == 50.0  # Copilot (30) + IADP (20)
        assert 65.0 <= result['dpi'] <= 75.0  # Weighted average
    
    def test_sample_scoring_team_c_needs_improvement(self, calculator):
        """
        Sample Scoring: Team C - Needs Improvement
        
        Team Profile:
        - Low deployment frequency (20/year)
        - Slow lead time (15 days)
        - Manual processes
        - Poor hygiene (40/100)
        - Compliance gaps
        - Limited adoption
        """
        metrics = {
            # Release Velocity
            'rf': 20, 'lttd': 15.0,
            # Pipeline Maturity
            'ci': True, 'cd': False, 'rollback': False,
            'zero_touch_deployment': False, 'pipeline_standard': False,
            # Git Hygiene
            'git_hygiene_score': 40.0,
            # Compliance
            'release_page_url': '',
            'compliance_evidence_page': '',
            'repo_docs': '',
            'is_priv_access_current': False,
            'cr_auto_creation': False,
            # Quality & Security
            'sast_enabled': False,
            'sonarqube_project': '',
            'data_classification': 'Public',
            # Adoption
            'copilot_enabled': False,
            'ai_tools_declared': False,
            'apis_published_iadp': False,
            'apis_published_apix': False,
            'ai_devops_onboarded': False
        }
        
        result = calculator.calculate_all_scores(metrics)
        
        # Expected scores
        assert result['Release_Velocity_Score'] <= 30.0  # Low RF + slow LTTD
        assert result['Git_Hygiene_Score'] == 40.0
        assert result['Pipeline_Maturity_Score'] == 20.0  # Only CI
        assert result['Compliance_Score'] == 0.0  # None met
        assert result['Quality_Security_Score'] == 0.0  # None met
        assert result['Adoption_Score'] == 0.0  # None met
        assert result['dpi'] <= 25.0  # Very low overall
    
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
