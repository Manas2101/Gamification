"""
Metrics calculation module for DPI and component scores
Implements scoring logic based on DevOps metrics
"""

import numpy as np
import random
from typing import Dict, List


class MetricsCalculator:
    """Calculate DPI and component scores from raw metrics"""
    
    @staticmethod
    def calculate_rf_score(rf: int) -> int:
        """
        Calculate Release Frequency score
        
        Args:
            rf: Release frequency (number of releases)
            
        Returns:
            Score between 5-35
        """
        if rf is None:
            return 5
        
        if rf >= 300:
            return 35
        elif rf >= 200:
            return 32
        elif rf >= 150:
            return 25
        elif rf >= 100:
            return 18
        elif rf >= 50:
            return 10
        else:
            return 5
    
    @staticmethod
    def calculate_flow_score(lttd: float, ltdd_measurable: float) -> int:
        """
        Calculate Flow score based on LTTD
        
        Args:
            lttd: Lead Time to Deploy (in days)
            ltdd_measurable: LTTD measurability percentage
            
        Returns:
            Score between 5-25 (capped at 10 if measurability < 90%)
        """
        if lttd is None:
            return 5
        
        base_score = 5
        if lttd <= 2:
            base_score = 25
        elif lttd <= 5:
            base_score = 20
        elif lttd <= 10:
            base_score = 15
        elif lttd <= 15:
            base_score = 10
        else:
            base_score = 5
        
        # Cap at 10 if measurability < 90%
        if ltdd_measurable is not None and ltdd_measurable < 0.90:
            base_score = min(base_score, 10)
        
        return base_score
    
    @staticmethod
    def calculate_cfr_score(cfr: float) -> int:
        """
        Calculate Change Failure Rate score
        
        Args:
            cfr: Change Failure Rate (0-1)
            
        Returns:
            Score between 1-7
        """
        if cfr is None:
            return 4
        
        if cfr <= 0.05:
            return 7
        elif cfr <= 0.10:
            return 7
        elif cfr <= 0.15:
            return 4
        elif cfr <= 0.20:
            return 4
        elif cfr <= 0.25:
            return 1
        else:
            return 1
    
    @staticmethod
    def calculate_mttr_score(mttr: float) -> int:
        """
        Calculate Mean Time To Restore score
        
        Args:
            mttr: MTTR in hours
            
        Returns:
            Score between 1-7
        """
        if mttr is None:
            return 4
        
        if mttr <= 1:
            return 7
        elif mttr <= 2:
            return 4
        else:
            return 1
    
    @staticmethod
    def calculate_priv_score(priv_access: int) -> int:
        """
        Calculate Privileged Access score
        
        Args:
            priv_access: Number of privileged access instances
            
        Returns:
            Score between 0-6
        """
        if priv_access == 0:
            return 0
        elif priv_access == 1:
            return 2
        elif priv_access == 2:
            return 4
        else:
            return 6
    
    @staticmethod
    def calculate_automation_score(ci: bool, cd: bool, iac: bool, 
                                   rollback: bool, self_service: bool) -> int:
        """
        Calculate Automation score
        
        Args:
            ci: CI enabled
            cd: CD enabled
            iac: Infrastructure as Code enabled
            rollback: Rollback capability
            self_service: Self-service enabled
            
        Returns:
            Score between 0-20
        """
        score = 0
        if ci:
            score += 5
        if cd:
            score += 3
        if iac:
            score += 4
        if rollback:
            score += 3
        if self_service:
            score += 5
        return score
    
    @staticmethod
    def calculate_stability_score(cfr_reported: bool, automation_audited: bool,
                                  critical_data_present: bool, cfr: float,
                                  mttr: float, ltdd_measurable: float) -> int:
        """
        Calculate Stability score
        
        Args:
            cfr_reported: CFR reporting status
            automation_audited: Automation audit status
            critical_data_present: Critical data presence
            cfr: Change Failure Rate
            mttr: Mean Time To Restore
            ltdd_measurable: LTTD measurability
            
        Returns:
            Score between 0-20
        """
        score = 0
        
        # Base points for reporting
        if cfr_reported:
            score += 2
        if automation_audited:
            score += 2
        if critical_data_present:
            score += 2
        
        # Performance-based points
        if cfr is not None and cfr <= 0.10:
            score += 4
        if mttr is not None and mttr <= 1:
            score += 5
        if ltdd_measurable is not None and ltdd_measurable >= 0.95:
            score += 5
        
        return min(score, 20)
    
    @staticmethod
    def calculate_dpi(rf_score: int, flow_score: int, cfr_score: int,
                     mttr_score: int, priv_score: int, automation_score: int,
                     stability_score: int) -> int:
        """
        Calculate DevOps Performance Index (DPI)
        
        Args:
            rf_score: Release Frequency score
            flow_score: Flow score
            cfr_score: CFR score
            mttr_score: MTTR score
            priv_score: Privileged Access score
            automation_score: Automation score
            stability_score: Stability score
            
        Returns:
            Total DPI score
        """
        return (rf_score + flow_score + cfr_score + mttr_score + 
                priv_score + automation_score + stability_score)
    
    @staticmethod
    def determine_tier(dpi: int) -> str:
        """
        Determine performance tier based on DPI
        
        Args:
            dpi: DevOps Performance Index
            
        Returns:
            Tier name
        """
        if dpi >= 85:
            return "Elite"
        elif dpi >= 70:
            return "Advanced"
        elif dpi >= 50:
            return "Emerging"
        else:
            return "Needs Support"
    
    @staticmethod
    def get_data_quality_flags(ltdd_measurable: float) -> List[str]:
        """
        Generate data quality flags
        
        Args:
            ltdd_measurable: LTTD measurability percentage
            
        Returns:
            List of quality flags
        """
        flags = []
        if ltdd_measurable is not None and ltdd_measurable < 0.90:
            flags.append("LTDD_Measurability<90% -> Flow capped")
        return flags
    
    @classmethod
    def calculate_all_scores(cls, metrics: Dict) -> Dict:
        """
        Calculate all scores and DPI from raw metrics
        
        Args:
            metrics: Dictionary containing raw metric values
            
        Returns:
            Dictionary with all calculated scores
        """
        # Calculate component scores
        rf_score = cls.calculate_rf_score(metrics.get('rf'))
        flow_score = cls.calculate_flow_score(
            metrics.get('lttd'), 
            metrics.get('ltdd_measurable')
        )
        cfr_score = cls.calculate_cfr_score(metrics.get('cfr'))
        mttr_score = cls.calculate_mttr_score(metrics.get('mttr'))
        priv_score = cls.calculate_priv_score(metrics.get('priv_access', 0))
        automation_score = cls.calculate_automation_score(
            metrics.get('ci', False),
            metrics.get('cd', False),
            metrics.get('iac', False),
            metrics.get('rollback', False),
            metrics.get('self_service', False)
        )
        stability_score = cls.calculate_stability_score(
            metrics.get('cfr_reported', True),
            metrics.get('automation_audited', True),
            metrics.get('critical_data_present', True),
            metrics.get('cfr'),
            metrics.get('mttr'),
            metrics.get('ltdd_measurable')
        )
        
        # Calculate DPI
        dpi = cls.calculate_dpi(
            rf_score, flow_score, cfr_score, mttr_score,
            priv_score, automation_score, stability_score
        )
        
        # Determine tier
        tier = cls.determine_tier(dpi)
        
        # Get quality flags
        data_quality_flags = cls.get_data_quality_flags(
            metrics.get('ltdd_measurable')
        )
        
        return {
            'rf_score': rf_score,
            'flow_score': flow_score,
            'cfr_score': cfr_score,
            'mttr_score': mttr_score,
            'priv_score': priv_score,
            'automation_score': automation_score,
            'stability_score': stability_score,
            'dpi': dpi,
            'tier': tier,
            'data_quality_flags': str(data_quality_flags)
        }
    
    @staticmethod
    def randomize_missing_fields() -> Dict:
        """
        Generate random values for fields not available from API
        
        Returns:
            Dictionary with randomized field values
        """
        stacks = ['Legacy', 'Cloud Native', 'Hybrid']
        business_units = ['BU A', 'BU B', 'BU C']
        
        return {
            'ltdd_measurable': round(random.uniform(0.85, 1.0), 2),
            'priv_access': random.randint(0, 3),
            'ci': random.choice([True, False]),
            'cd': random.choice([True, False]),
            'iac': random.choice([True, False]),
            'rollback': random.choice([True, False]),
            'self_service': random.choice([True, False]),
            'cfr_reported': True,
            'automation_audited': True,
            'critical_data_present': True,
            'stack': random.choice(stacks),
            'business_unit': random.choice(business_units)
        }
