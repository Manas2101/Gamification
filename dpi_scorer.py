"""
DPI Scoring Module - 6 Pillar System (0-100 scale)
Calculates DevOps Performance Index using YAML registry + DataSight API metrics

Pillars:
  1. Velocity (30%) - Release frequency, deployment speed
  2. Flow (20%) - Lead time, deployment efficiency  
  3. Stability (20%) - CFR, MTTR, reliability
  4. Automation (15%) - CI/CD, pipeline maturity
  5. Quality & Security (10%) - SAST, data classification
  6. AI & Adoption (5%) - Copilot, API catalog
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class DPIScorer:
    """Calculate 6-pillar DPI scores (0-100 scale)"""
    
    @staticmethod
    def calculate_velocity_score(rf: int, app_type: str, tier: int) -> float:
        """
        Velocity pillar (30% of total)
        Based on release frequency
        
        Args:
            rf: Release frequency (releases per month)
            app_type: App type (modern/traditional/legacy/vendor)
            tier: App tier (1=critical, 2=important, 3=standard)
        
        Returns:
            Score 0-100 for this pillar
        """
        if rf is None:
            rf = 0
        
        # Vendor apps excluded from RF scoring
        if app_type == "vendor":
            return 50.0  # Neutral score
        
        # Tier-based targets
        if tier == 1:
            target = 20  # Tier 1: 20 releases/month = 100%
        elif tier == 2:
            target = 12  # Tier 2: 12 releases/month = 100%
        else:
            target = 8   # Tier 3: 8 releases/month = 100%
        
        # Linear scale: 0 releases = 0%, target releases = 100%
        score = min(100.0, (rf / target) * 100)
        
        return round(score, 1)
    
    @staticmethod
    def calculate_flow_score(lttd: float) -> float:
        """
        Flow pillar (20% of total)
        Based on Lead Time to Deploy
        
        Args:
            lttd: Lead time to deploy in days
        
        Returns:
            Score 0-100 for this pillar
        """
        if lttd is None:
            return 50.0  # Neutral if no data
        
        # Scoring scale:
        # <=1 day = 100%
        # <=2 days = 90%
        # <=5 days = 70%
        # <=10 days = 40%
        # >10 days = linear decline to 0% at 30 days
        
        if lttd <= 1:
            return 100.0
        elif lttd <= 2:
            return 90.0
        elif lttd <= 5:
            return 70.0
        elif lttd <= 10:
            return 40.0
        elif lttd <= 30:
            # Linear: 40% at 10 days, 0% at 30 days
            return round(40.0 - ((lttd - 10) / 20) * 40, 1)
        else:
            return 0.0
    
    @staticmethod
    def calculate_stability_score(cfr: float, mttr: float) -> float:
        """
        Stability pillar (20% of total)
        Based on Change Failure Rate and Mean Time to Restore
        
        Args:
            cfr: Change failure rate (0-1)
            mttr: Mean time to restore in hours
        
        Returns:
            Score 0-100 for this pillar
        """
        cfr_score = 50.0
        mttr_score = 50.0
        
        # CFR scoring (50% of pillar)
        if cfr is not None:
            if cfr <= 0.05:
                cfr_score = 100.0
            elif cfr <= 0.10:
                cfr_score = 85.0
            elif cfr <= 0.15:
                cfr_score = 65.0
            elif cfr <= 0.20:
                cfr_score = 40.0
            elif cfr <= 0.30:
                cfr_score = 20.0
            else:
                cfr_score = 0.0
        
        # MTTR scoring (50% of pillar)
        if mttr is not None:
            if mttr <= 1:
                mttr_score = 100.0
            elif mttr <= 2:
                mttr_score = 80.0
            elif mttr <= 4:
                mttr_score = 60.0
            elif mttr <= 8:
                mttr_score = 40.0
            elif mttr <= 24:
                mttr_score = 20.0
            else:
                mttr_score = 0.0
        
        # Average CFR and MTTR scores
        total = (cfr_score * 0.5) + (mttr_score * 0.5)
        return round(total, 1)
    
    @staticmethod
    def calculate_automation_score(ci: bool, cd: bool, standard_pipeline: bool,
                                   zero_touch: bool, automated_rollback: bool,
                                   feature_flags: bool, approval_gates: int) -> float:
        """
        Automation pillar (15% of total)
        Based on pipeline maturity flags
        
        Args:
            ci: CI automated
            cd: CD automated
            standard_pipeline: Standard pipeline adopted
            zero_touch: Zero-touch deployment
            automated_rollback: Automated rollback enabled
            feature_flags: Feature flags adopted
            approval_gates: Number of manual approval gates
        
        Returns:
            Score 0-100 for this pillar
        """
        score = 0.0
        
        # Core automation (60 points)
        if ci:
            score += 20
        if cd:
            score += 20
        if standard_pipeline:
            score += 20
        
        # Advanced automation (40 points)
        if zero_touch:
            score += 15
        if automated_rollback:
            score += 10
        if feature_flags:
            score += 15
        
        # Penalty for approval gates (each gate -10 points, max -30)
        gate_penalty = min(30, approval_gates * 10)
        score = max(0, score - gate_penalty)
        
        return round(score, 1)
    
    @staticmethod
    def calculate_quality_security_score(sast_enabled: bool, data_classification: str,
                                         priv_access_for_deploy: bool) -> float:
        """
        Quality & Security pillar (10% of total)
        Based on security practices
        
        Args:
            sast_enabled: SAST/DAST enabled
            data_classification: Data sensitivity (public/internal/restricted/confidential)
            priv_access_for_deploy: Requires privileged access for deploy
        
        Returns:
            Score 0-100 for this pillar
        """
        score = 0.0
        
        # SAST enabled (40 points)
        if sast_enabled:
            score += 40
        
        # Data classification appropriate (30 points)
        if data_classification in ["public", "internal"]:
            score += 30
        elif data_classification == "restricted":
            score += 20
        elif data_classification == "confidential":
            score += 10
        
        # No privileged access required (30 points)
        if not priv_access_for_deploy:
            score += 30
        
        return round(score, 1)
    
    @staticmethod
    def calculate_ai_adoption_score(copilot_enabled: bool, ai_tools_count: int,
                                   ai_test_generation: bool, apis_published: bool) -> float:
        """
        AI & Adoption pillar (5% of total)
        Based on AI tool usage and API publishing
        
        Args:
            copilot_enabled: GitHub Copilot enabled
            ai_tools_count: Number of AI tools declared
            ai_test_generation: AI test generation used
            apis_published: APIs published to catalog
        
        Returns:
            Score 0-100 for this pillar
        """
        score = 0.0
        
        # Copilot enabled (40 points)
        if copilot_enabled:
            score += 40
        
        # AI tools declared (20 points)
        if ai_tools_count > 0:
            score += min(20, ai_tools_count * 10)
        
        # AI test generation (20 points)
        if ai_test_generation:
            score += 20
        
        # APIs published (20 points)
        if apis_published:
            score += 20
        
        return round(min(100.0, score), 1)
    
    @classmethod
    def calculate_dpi(cls, metrics: Dict) -> Dict:
        """
        Calculate complete DPI with all 6 pillars
        
        Args:
            metrics: Dictionary with YAML + API metrics
        
        Returns:
            Dictionary with pillar scores and total DPI (0-100)
        """
        # Calculate each pillar (0-100 scale)
        velocity = cls.calculate_velocity_score(
            metrics.get('rf', 0),
            metrics.get('app_type', 'traditional'),
            metrics.get('tier', 2)
        )
        
        flow = cls.calculate_flow_score(
            metrics.get('lttd')
        )
        
        stability = cls.calculate_stability_score(
            metrics.get('cfr'),
            metrics.get('mttr')
        )
        
        automation = cls.calculate_automation_score(
            metrics.get('ci', False),
            metrics.get('cd', False),
            metrics.get('standard_pipeline_adopted', False),
            metrics.get('zero_touch_deployment', False),
            metrics.get('automated_rollback', False),
            metrics.get('feature_flags_adopted', False),
            metrics.get('approval_gate_count', 0)
        )
        
        quality_security = cls.calculate_quality_security_score(
            metrics.get('sast_enabled', False),
            metrics.get('data_classification', 'internal'),
            metrics.get('priv_access_for_deploy', True)
        )
        
        ai_adoption = cls.calculate_ai_adoption_score(
            metrics.get('copilot_enabled', False),
            len(metrics.get('ai_tools_declared', [])),
            metrics.get('ai_test_generation', False),
            metrics.get('apis_published', False)
        )
        
        # Calculate weighted DPI (0-100)
        dpi = (
            velocity * 0.30 +
            flow * 0.20 +
            stability * 0.20 +
            automation * 0.15 +
            quality_security * 0.10 +
            ai_adoption * 0.05
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
            'velocity': velocity,
            'flow': flow,
            'stability': stability,
            'automation': automation,
            'quality_security': quality_security,
            'ai_adoption': ai_adoption,
            # Legacy field names for backward compatibility
            'rf_score': int(velocity * 0.35),  # Approximate mapping
            'flow_score': int(flow * 0.25),
            'cfr_score': int(stability * 0.07),
            'mttr_score': int(stability * 0.07),
            'automation_score': int(automation * 0.20),
            'stability_score': int(stability * 0.20),
        }
