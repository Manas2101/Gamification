"""
Metrics Calculator
==================

Calculates DevOps Performance Index (DPI) scores across six pillars.

The six pillars are:
    1. Release Velocity - Deployment frequency and lead time
    2. Git Hygiene - Repository health and PR practices
    3. Pipeline Maturity - CI/CD automation level
    4. Compliance - Regulatory and documentation compliance
    5. Quality & Security - Code quality and security practices
    6. Adoption - Modern tooling and practices adoption

Example:
    >>> from src.core.calculator import MetricsCalculator
    >>> calc = MetricsCalculator()
    >>> scores = calc.calculate_all_scores(metrics_dict)

Author: DevOps Transformation Team
"""

import logging
from typing import Dict, Optional

# Configure module logger
logger = logging.getLogger(__name__)


class MetricsCalculator:
    """
    Calculator for 6-pillar DevOps Performance Index (DPI).
    
    Computes individual pillar scores and weighted overall DPI score.
    Each pillar is scored 0-100, and DPI is a weighted average.
    
    Attributes:
        WEIGHTS (dict): Weight for each pillar in DPI calculation
        
    Example:
        >>> calc = MetricsCalculator()
        >>> result = calc.calculate_all_scores(metrics)
        >>> print(f"DPI Score: {result['dpi']}")
    """
    
    # Pillar weights for DPI calculation (must sum to 1.0)
    WEIGHTS = {
        'release_velocity': 0.20,
        'git_hygiene': 0.15,
        'pipeline_maturity': 0.20,
        'compliance': 0.15,
        'quality_security': 0.15,
        'adoption': 0.15
    }
    
    # Scoring thresholds
    RF_EXCELLENT = 20      # Release frequency for max score
    RF_GOOD = 10           # Release frequency for good score
    LTTD_EXCELLENT = 1.0   # Lead time (days) for max score
    LTTD_GOOD = 3.0        # Lead time (days) for good score
    
    def __init__(self):
        """Initialize the metrics calculator."""
        logger.info("MetricsCalculator initialized")
    
    def _safe_get(self, metrics: Dict, key: str, default=None):
        """
        Safely get value from metrics dict.
        
        Args:
            metrics: Metrics dictionary.
            key: Key to retrieve.
            default: Default value if key not found or value is None.
            
        Returns:
            Value from dict or default.
        """
        value = metrics.get(key)
        return value if value is not None else default
    
    def calculate_release_velocity(self, metrics: Dict) -> float:
        """
        Calculate Release Velocity pillar score (0-100).
        
        Components:
            - Release Frequency (RF): 50% weight
            - Lead Time to Deploy (LTTD): 50% weight
        
        Args:
            metrics: Dictionary containing rf, lttd.
            
        Returns:
            Release Velocity score (0-100).
        """
        score = 0.0
        
        # Release Frequency component (50%)
        rf = self._safe_get(metrics, 'rf', 0)
        if rf >= self.RF_EXCELLENT:
            rf_score = 100
        elif rf >= self.RF_GOOD:
            rf_score = 70 + (rf - self.RF_GOOD) * 3
        elif rf > 0:
            rf_score = rf * 7
        else:
            rf_score = 0
        score += rf_score * 0.5
        
        # Lead Time to Deploy component (50%)
        lttd = self._safe_get(metrics, 'lttd', 0)
        if lttd <= 0:
            lttd_score = 50  # No data - neutral score
        elif lttd <= self.LTTD_EXCELLENT:
            lttd_score = 100
        elif lttd <= self.LTTD_GOOD:
            lttd_score = 100 - (lttd - self.LTTD_EXCELLENT) * 15
        else:
            lttd_score = max(0, 70 - (lttd - self.LTTD_GOOD) * 10)
        score += lttd_score * 0.5
        
        return round(min(100, max(0, score)), 2)
    
    def calculate_git_hygiene(self, metrics: Dict) -> float:
        """
        Calculate Git Hygiene pillar score (0-100).
        
        Uses pre-calculated hygiene score from GitHub analysis.
        Falls back to default score if not available.
        
        Args:
            metrics: Dictionary containing git_hygiene_score.
            
        Returns:
            Git Hygiene score (0-100).
        """
        score = self._safe_get(metrics, 'git_hygiene_score')
        
        if score is not None:
            return round(min(100, max(0, score)), 2)
        
        # Default score when no data available
        logger.debug("No git hygiene score available, using default")
        return 50.0
    
    def calculate_pipeline_maturity(self, metrics: Dict) -> float:
        """
        Calculate Pipeline Maturity pillar score (0-100).
        
        Components:
            - CI enabled: 20%
            - CD enabled: 20%
            - Automated rollback: 20%
            - Self-service deployment: 20%
            - Pipeline standardization: 20%
        
        Args:
            metrics: Dictionary containing ci, cd, rollback, self_service, pipeline_standard.
            
        Returns:
            Pipeline Maturity score (0-100).
        """
        score = 0.0
        
        # Each component worth 20 points
        if self._safe_get(metrics, 'ci', False):
            score += 20
        if self._safe_get(metrics, 'cd', False):
            score += 20
        if self._safe_get(metrics, 'rollback', False):
            score += 20
        if self._safe_get(metrics, 'self_service', False):
            score += 20
        if self._safe_get(metrics, 'pipeline_standard', False):
            score += 20
        
        return round(score, 2)
    
    def calculate_compliance(self, metrics: Dict) -> float:
        """
        Calculate Compliance pillar score (0-100).
        
        Components:
            - Release page URL documented: 20%
            - Compliance evidence page: 20%
            - Repo documentation present (repo_docs): 20%
            - Privileged access current: 20%
            - CR auto-creation enabled: 20%
        
        Args:
            metrics: Dictionary containing release_page_url, compliance_evidence_page,
                    repo_docs, is_priv_access_current, cr_auto_creation.
            
        Returns:
            Compliance score (0-100).
        """
        score = 0.0
        
        # Each component now worth 20 points (5 components)
        if self._safe_get(metrics, 'release_page_url'):
            score += 20
        if self._safe_get(metrics, 'compliance_evidence_page'):
            score += 20
        # repo_docs may be a boolean or URL/path; treat truthy as present
        if self._safe_get(metrics, 'repo_docs'):
            score += 20
        if self._safe_get(metrics, 'is_priv_access_current', False):
            score += 20
        if self._safe_get(metrics, 'cr_auto_creation', False):
            score += 20
        
        return round(min(100, score), 2)
    
    def calculate_quality_security(self, metrics: Dict) -> float:
        """
        Calculate Quality & Security pillar score (0-100).
        
        Components:
            - SAST enabled: 35%
            - SonarQube integration: 35%
            - Data classification defined: 30%
        
        Args:
            metrics: Dictionary containing sast_enabled, sonarqube_project,
                    data_classification.
            
        Returns:
            Quality & Security score (0-100).
        """
        score = 0.0
        
        if self._safe_get(metrics, 'sast_enabled', False):
            score += 35
        
        if self._safe_get(metrics, 'sonarqube_project'):
            score += 35
        
        data_class = self._safe_get(metrics, 'data_classification', '')
        if data_class and data_class.lower() not in ['', 'none', 'public']:
            score += 30
        
        return round(score, 2)
    
    def calculate_adoption(self, metrics: Dict) -> float:
        """
        Calculate Adoption pillar score (0-100).
        
        Components:
            - Copilot enabled: 30%
            - AI tools declared: 10%
            - APIs published (IADP): up to 20%
            - APIs published (APIX): up to 20%
            - AI DevOps onboarding completed (ai_devops_onboarded): 20%
            # Feature flags currently omitted/commented out
        
        Args:
            metrics: Dictionary containing copilot_enabled, ai_tools_declared,
                    apis_published_iadp, apis_published_apix, ai_devops_onboarded.
            
        Returns:
            Adoption score (0-100).
        """
        score = 0.0
        
        if self._safe_get(metrics, 'copilot_enabled', False):
            score += 30
        
        # AI tools declared is now worth 10 points
        if self._safe_get(metrics, 'ai_tools_declared', False):
            score += 10
        
        # New API scoring: split into two categories with separate caps
        iadp_apis = int(self._safe_get(metrics, 'apis_published_iadp', 0) or 0)
        apix_apis = int(self._safe_get(metrics, 'apis_published_apix', 0) or 0)
        
        # IADP: 1 API = 10 points, cap 20 points
        if iadp_apis > 0:
            score += min(20, iadp_apis * 10)
        
        # APIX: 1 API = 10 points, cap 20 points
        if apix_apis > 0:
            score += min(20, apix_apis * 10)
        
        # AI DevOps onboarding: boolean flag worth 20 points
        if self._safe_get(metrics, 'ai_devops_onboarded', False):
            score += 20
        
        # feature_flags_adopted intentionally omitted (commented out)
        
        return round(min(100, score), 2)
    
    def calculate_dpi(
        self, 
        release_velocity: float,
        git_hygiene: float,
        pipeline_maturity: float,
        compliance: float,
        quality_security: float,
        adoption: float
    ) -> float:
        """
        Calculate overall DPI score as weighted average.
        
        Args:
            release_velocity: Release Velocity pillar score.
            git_hygiene: Git Hygiene pillar score.
            pipeline_maturity: Pipeline Maturity pillar score.
            compliance: Compliance pillar score.
            quality_security: Quality & Security pillar score.
            adoption: Adoption pillar score.
            
        Returns:
            Overall DPI score (0-100).
        """
        dpi = (
            release_velocity * self.WEIGHTS['release_velocity'] +
            git_hygiene * self.WEIGHTS['git_hygiene'] +
            pipeline_maturity * self.WEIGHTS['pipeline_maturity'] +
            compliance * self.WEIGHTS['compliance'] +
            quality_security * self.WEIGHTS['quality_security'] +
            adoption * self.WEIGHTS['adoption']
        )
        
        return round(dpi, 2)
    
    def calculate_all_scores(self, metrics: Dict) -> Dict[str, float]:
        """
        Calculate all pillar scores and overall DPI.
        
        This is the main entry point for score calculation.
        
        Args:
            metrics: Dictionary containing all metric values.
            
        Returns:
            Dictionary with all pillar scores and DPI:
            {
                'Release_Velocity_Score': float,
                'Git_Hygiene_Score': float,
                'Pipeline_Maturity_Score': float,
                'Compliance_Score': float,
                'Quality_Security_Score': float,
                'Adoption_Score': float,
                'dpi': float
            }
        """
        # Calculate individual pillar scores
        release_velocity = self.calculate_release_velocity(metrics)
        git_hygiene = self.calculate_git_hygiene(metrics)
        pipeline_maturity = self.calculate_pipeline_maturity(metrics)
        compliance = self.calculate_compliance(metrics)
        quality_security = self.calculate_quality_security(metrics)
        adoption = self.calculate_adoption(metrics)
        
        # Calculate overall DPI
        dpi = self.calculate_dpi(
            release_velocity,
            git_hygiene,
            pipeline_maturity,
            compliance,
            quality_security,
            adoption
        )
        
        result = {
            'Release_Velocity_Score': release_velocity,
            'Git_Hygiene_Score': git_hygiene,
            'Pipeline_Maturity_Score': pipeline_maturity,
            'Compliance_Score': compliance,
            'Quality_Security_Score': quality_security,
            'Adoption_Score': adoption,
            'dpi': dpi
        }
        
        logger.debug(f"Calculated scores: DPI={dpi}")
        return result
