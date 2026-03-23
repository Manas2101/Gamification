"""
Metrics calculation module for DPI and component scores
Implements NEW 6-pillar scoring system (0-100 scale)

Pillars:
1. Release Velocity (30%) - RF + LTTD + zero-touch bonus
2. Git Hygiene (20%) - From hygiene_checker.py output
3. Pipeline Maturity (20%) - CI/CD flags + pipeline standard
4. Compliance (15%) - Release page + evidence + priv access + data classification
5. Quality & Security (10%) - SonarQube or hygiene violations
6. Adoption (5%) - API catalog + AI tools + pipeline v2+
"""

from typing import Dict, Optional


class MetricsCalculator:
    """Calculate DPI and 6-pillar scores from raw metrics"""
    
    # Pillar weights (must sum to 100)
    WEIGHTS = {
        "release_velocity": 30,
        "git_hygiene": 20,
        "pipeline_maturity": 20,
        "compliance": 15,
        "quality_security": 10,
        "adoption": 5,
    }
    
    @staticmethod
    def calculate_release_velocity_score(rf: int, lttd: float, app_type: str, 
                                         tier: int, zero_touch: bool) -> float:
        """
        Release Velocity pillar (30% of total)
        Combines RF (60%) + LTTD (40%) + zero-touch bonus (+5)
        
        Args:
            rf: Release frequency (releases per month)
            lttd: Lead time to deploy in days
            app_type: App type (modern/traditional/legacy/vendor)
            tier: App tier (1=critical, 2=important, 3=standard)
            zero_touch: Zero-touch deployment enabled
        
        Returns:
            Score 0-100 for this pillar
        """
        if rf is None:
            rf = 0
        
        # Vendor apps excluded from RF scoring
        if app_type == "vendor":
            return 50.0  # Neutral score
        
        # RF Score (60% of pillar) - Tier-based targets
        if tier == 1:
            target = 20  # Tier 1: 20 releases/month = 100%
        elif tier == 2:
            target = 12  # Tier 2: 12 releases/month = 100%
        else:
            target = 8   # Tier 3: 8 releases/month = 100%
        
        freq_score = min(100.0, (rf / target) * 100)
        
        # LTTD Score (40% of pillar) - Target: <=1.8 days = 100%
        if lttd is not None:
            if lttd <= 1.8:
                lttd_score = 100.0
            elif lttd >= 8:
                lttd_score = 0.0
            else:
                # Linear scale: 1.8 days=100, 8 days=0
                lttd_score = max(0, min(100, (8 - lttd) / (8 - 1.8) * 100))
        else:
            lttd_score = 50.0  # Neutral if no data
        
        # Zero-touch bonus: +5 bonus points
        zero_touch_bonus = 5 if zero_touch else 0
        
        # Combine: 60% RF + 40% LTTD + bonus
        raw = (freq_score * 0.6) + (lttd_score * 0.4) + zero_touch_bonus
        
        return round(min(100.0, raw), 1)
    
    @staticmethod
    def calculate_git_hygiene_score(hygiene_score: Optional[float], 
                                    critical_violations: int = 0,
                                    warning_violations: int = 0) -> float:
        """
        Git Hygiene pillar (20% of total)
        Uses score from hygiene_checker.py output
        
        Args:
            hygiene_score: Score from hygiene_checker.py (0-100), or None
            critical_violations: Count of critical violations (fallback)
            warning_violations: Count of warning violations (fallback)
        
        Returns:
            Score 0-100 for this pillar
        """
        # If we have hygiene_checker.py score, use it directly
        if hygiene_score is not None:
            return round(hygiene_score, 1)
        
        # Fallback: calculate from violation counts
        # Each critical violation deducts 10 points, warnings deduct 5
        deduction = (critical_violations * 10) + (warning_violations * 5)
        score = max(0, 100 - deduction)
        
        return round(score, 1)
    
    @staticmethod
    def calculate_pipeline_maturity_score(ci: bool, cd: bool, cr_auto_creation: bool,
                                         feature_flags: bool, pipeline_standard: str,
                                         zero_touch: bool) -> float:
        """
        Pipeline Maturity pillar (20% of total)
        Based on CI/CD capabilities and automation flags
        
        Args:
            ci: CI pipeline configured
            cd: CD pipeline enabled
            cr_auto_creation: Change requests auto-created
            feature_flags: Feature flags adopted
            pipeline_standard: Pipeline standard version ("v1" or "v2")
            zero_touch: Zero-touch deployment
        
        Returns:
            Score 0-100 for this pillar
        """
        score = 0.0
        
        # CI exists (20 pts)
        if ci:
            score += 20
        
        # CD enabled (25 pts)
        if cd:
            score += 25
        
        # CR auto-creation (20 pts)
        if cr_auto_creation:
            score += 20
        
        # Feature flags (15 pts)
        if feature_flags:
            score += 15
        
        # Pipeline standard version (10 pts — v2+ = full, v1 = half)
        try:
            std_ver = int(str(pipeline_standard).lstrip("v") or "1")
        except (ValueError, AttributeError):
            std_ver = 1
        
        if std_ver >= 2:
            score += 10
        elif std_ver == 1:
            score += 5
        
        # Zero-touch (10 pts)
        if zero_touch:
            score += 10
        
        return round(min(100.0, score), 1)
    
    @staticmethod
    def calculate_compliance_score(has_release_page: bool, has_compliance_evidence: bool,
                                   priv_access_current: bool, data_classification: str,
                                   tier: int) -> float:
        """
        Compliance pillar (15% of total)
        Based on compliance fields in registry
        
        Args:
            has_release_page: Release page URL declared
            has_compliance_evidence: Compliance evidence linked
            priv_access_current: Privileged access reviewed <90 days ago
            data_classification: Data classification declared
            tier: App tier (1=critical requires evidence)
        
        Returns:
            Score 0-100 for this pillar
        """
        score = 0.0
        
        # Release page exists (30 pts)
        if has_release_page:
            score += 30
        
        # Compliance evidence (25 pts — Tier 1 required, others optional)
        if tier == 1:
            if has_compliance_evidence:
                score += 25
            # CRITICAL: Tier-1 app missing compliance evidence = 0 points
        else:
            if has_compliance_evidence:
                score += 15
        
        # Privileged access reviewed (30 pts)
        if priv_access_current:
            score += 30
        
        # Data classification declared (15 pts)
        if data_classification and data_classification != "internal":
            score += 15
        
        return round(min(100.0, score), 1)
    
    @staticmethod
    def calculate_quality_security_score(sast_enabled: bool, 
                                         hygiene_score: Optional[float] = None,
                                         critical_violations: int = 0,
                                         warning_violations: int = 0) -> float:
        """
        Quality & Security pillar (10% of total)
        Uses SonarQube if available, falls back to hygiene violations
        
        Args:
            sast_enabled: SAST/DAST enabled
            hygiene_score: Score from hygiene_checker.py (0-100), or None
            critical_violations: Count of critical violations (fallback)
            warning_violations: Count of warning violations (fallback)
        
        Returns:
            Score 0-100 for this pillar
        """
        # SAST enabled gives base 40 points
        score = 40.0 if sast_enabled else 0.0
        
        # If we have hygiene score, use it for remaining 60 points
        if hygiene_score is not None:
            # Scale hygiene score (0-100) to 60 points
            score += (hygiene_score / 100) * 60
        else:
            # Fallback: use violation counts
            # Each violation deducts from 60 points
            deduction = (critical_violations * 2) + warning_violations
            remaining = max(0, 60 - (deduction * 5))
            score += remaining
        
        return round(min(100.0, score), 1)
    
    @staticmethod
    def calculate_adoption_score(apis_published: bool, ai_tools_declared: list,
                                 copilot_enabled: bool, pipeline_standard: str) -> float:
        """
        Adoption pillar (5% of total)
        Based on API catalog, AI tools, and pipeline standards
        
        Args:
            apis_published: APIs published in catalog
            ai_tools_declared: List of AI tools declared
            copilot_enabled: GitHub Copilot enabled
            pipeline_standard: Pipeline standard version ("v1" or "v2")
        
        Returns:
            Score 0-100 for this pillar
        """
        score = 0.0
        
        # API catalog published (40 pts)
        if apis_published:
            score += 40
        
        # AI tools declared (40 pts — any tool = full score)
        has_ai = bool(ai_tools_declared or copilot_enabled)
        if has_ai:
            score += 40
        
        # Pipeline standard v2+ (20 pts)
        try:
            std_ver = int(str(pipeline_standard).lstrip("v") or "1")
        except (ValueError, AttributeError):
            std_ver = 1
        
        if std_ver >= 2:
            score += 20
        
        return round(min(100.0, score), 1)
    
    @classmethod
    def calculate_all_scores(cls, metrics: Dict) -> Dict:
        """
        Calculate complete DPI with NEW 6 pillars (0-100 scale)
        
        Pillars:
        1. Release Velocity (30%) - RF + LTTD + zero-touch
        2. Git Hygiene (20%) - From hygiene_checker.py
        3. Pipeline Maturity (20%) - CI/CD + pipeline standard
        4. Compliance (15%) - Release page + evidence + priv access
        5. Quality & Security (10%) - SAST + hygiene
        6. Adoption (5%) - APIs + AI tools + pipeline v2
        
        Args:
            metrics: Dictionary with YAML + API + hygiene metrics
        
        Returns:
            Dictionary with pillar scores and total DPI (0-100)
        """
        # 1. Release Velocity (30%)
        release_velocity = cls.calculate_release_velocity_score(
            metrics.get('rf', 0),
            metrics.get('lttd'),
            metrics.get('app_type', 'traditional'),
            metrics.get('tier', 2),
            metrics.get('zero_touch_deployment', False)
        )
        
        # 2. Git Hygiene (20%)
        git_hygiene = cls.calculate_git_hygiene_score(
            metrics.get('git_hygiene_score'),
            metrics.get('git_hygiene_violations_critical', 0),
            metrics.get('git_hygiene_violations_warnings', 0)
        )
        
        # 3. Pipeline Maturity (20%)
        pipeline_maturity = cls.calculate_pipeline_maturity_score(
            metrics.get('ci', False),
            metrics.get('cd', False),
            metrics.get('cr_auto_creation', False),
            metrics.get('feature_flags_adopted', False),
            metrics.get('pipeline_standard', 'v1'),
            metrics.get('zero_touch_deployment', False)
        )
        
        # 4. Compliance (15%)
        compliance = cls.calculate_compliance_score(
            metrics.get('has_release_page', False),
            metrics.get('has_compliance_evidence', False),
            metrics.get('is_priv_access_current', False),
            metrics.get('data_classification', 'internal'),
            metrics.get('tier', 2)
        )
        
        # 5. Quality & Security (10%)
        quality_security = cls.calculate_quality_security_score(
            metrics.get('sast_enabled', False),
            metrics.get('git_hygiene_score'),
            metrics.get('git_hygiene_violations_critical', 0),
            metrics.get('git_hygiene_violations_warnings', 0)
        )
        
        # 6. Adoption (5%)
        adoption = cls.calculate_adoption_score(
            metrics.get('apis_published', False),
            metrics.get('ai_tools_declared', []),
            metrics.get('copilot_enabled', False),
            metrics.get('pipeline_standard', 'v1')
        )
        
        # Calculate weighted DPI (0-100)
        dpi = (
            release_velocity * 0.30 +
            git_hygiene * 0.20 +
            pipeline_maturity * 0.20 +
            compliance * 0.15 +
            quality_security * 0.10 +
            adoption * 0.05
        )
        
        # Determine tier
        if dpi >= 85:
            tier = "Elite"
        elif dpi >= 70:
            tier = "Advanced"
        elif dpi >= 55:
            tier = "Emerging"
        else:
            tier = "Needs Support"
        
        return {
            'dpi': round(dpi, 1),
            'tier': tier,
            # New 6 pillars (raw scores 0-100)
            'release_velocity_score': release_velocity,
            'git_hygiene_score': git_hygiene,
            'pipeline_maturity_score': pipeline_maturity,
            'compliance_score': compliance,
            'quality_security_score': quality_security,
            'adoption_score': adoption,
            # Weighted contributions (for transparency)
            'release_velocity_weighted': round(release_velocity * 0.30, 2),
            'git_hygiene_weighted': round(git_hygiene * 0.20, 2),
            'pipeline_maturity_weighted': round(pipeline_maturity * 0.20, 2),
            'compliance_weighted': round(compliance * 0.15, 2),
            'quality_security_weighted': round(quality_security * 0.10, 2),
            'adoption_weighted': round(adoption * 0.05, 2),
            # Legacy field names for backward compatibility (keep for transition)
            'velocity': release_velocity,
            'flow': release_velocity,  # Flow merged into Release Velocity
            'stability': compliance,  # Stability merged into Compliance
            'automation': pipeline_maturity,
            'quality_security': quality_security,
            'ai_adoption': adoption,
            'data_quality_flags': ''
        }
