"""
Simplified recommendation helper for the gamification dashboard
Integrates with the recommendation.py engine but provides a simpler interface
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class RecommendationHelper:
    """Simplified interface to get recommendations for apps"""
    
    def __init__(self):
        """Initialize recommendation helper"""
        self.engine = None
        self._init_engine()
    
    def _init_engine(self):
        """Initialize the recommendation engine if available"""
        try:
            from recommendation import RecommendationEngine
            
            # Check if rules file exists
            rules_path = Path(__file__).parent / "config" / "recommendation_rules.yaml"
            if rules_path.exists():
                self.engine = RecommendationEngine(rules_path)
                logger.info("Recommendation engine initialized successfully")
            else:
                logger.warning(f"Recommendation rules not found at {rules_path}")
        except Exception as e:
            logger.warning(f"Could not initialize recommendation engine: {e}")
    
    def get_recommendations(self, app_data: Dict, score_data: Dict, max_recommendations: int = 3) -> List[Dict]:
        """
        Get recommendations for an app
        
        Args:
            app_data: App registry data (from YAML)
            score_data: Calculated scores and DPI
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            List of recommendation dictionaries
        """
        if not self.engine:
            return self._get_fallback_recommendations(app_data, score_data, max_recommendations)
        
        try:
            # Build registry entry format expected by recommendation engine
            registry_entry = self._build_registry_entry(app_data)
            
            # Build score dict format
            score_dict = self._build_score_dict(score_data)
            
            # Get recommendations from engine
            recommendations = self.engine.get_recommendations(
                registry_entry,
                score_dict,
                max_total=max_recommendations
            )
            
            # Convert to simple dict format
            return [
                {
                    'action': rec.action,
                    'detail': rec.detail,
                    'pillar': rec.pillar,
                    'effort': rec.effort,
                    'effort_emoji': rec.effort_emoji,
                    'points_gain': rec.points_gain,
                    'source': rec.source
                }
                for rec in recommendations
            ]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return self._get_fallback_recommendations(app_data, score_data, max_recommendations)
    
    def _build_registry_entry(self, app_data: Dict) -> Dict:
        """Convert app data to registry entry format"""
        # Handle both flat and nested YAML formats
        pipeline_flags = app_data.get('pipeline_flags', {})
        access_security = app_data.get('access_security', {})
        compliance = app_data.get('compliance', {})
        ai_adoption = app_data.get('ai_adoption', {})
        
        return {
            'app_id': app_data.get('eim', app_data.get('pod_id')),
            'app_name': app_data.get('app_name', app_data.get('pod_name')),
            'app_type': app_data.get('app_type', 'traditional'),
            'tier': app_data.get('tier', 2),
            'in_production': app_data.get('in_production', True),
            'stack': app_data.get('stack', ''),
            
            'pipeline_flags': {
                'ci_automated': pipeline_flags.get('ci_automated', app_data.get('ci_automated', app_data.get('ci', False))),
                'cd_automated': pipeline_flags.get('cd_automated', app_data.get('cd_automated', app_data.get('cd', False))),
                'git_hygiene_adopted': pipeline_flags.get('git_hygiene_adopted', app_data.get('git_hygiene_adopted', False)),
                'cr_auto_creation': pipeline_flags.get('cr_auto_creation', app_data.get('cr_auto_creation', False)),
                'zero_touch_deployment': pipeline_flags.get('zero_touch_deployment', app_data.get('zero_touch_deployment', app_data.get('self_service', False))),
                'automated_rollback': pipeline_flags.get('automated_rollback', app_data.get('automated_rollback', app_data.get('rollback', False))),
                'feature_flags_adopted': pipeline_flags.get('feature_flags_adopted', app_data.get('feature_flags_adopted', False)),
                'approval_gate_count': pipeline_flags.get('approval_gate_count', app_data.get('approval_gate_count', 0)),
                'standard_pipeline_adopted': pipeline_flags.get('standard_pipeline_adopted', app_data.get('standard_pipeline_adopted', False)),
            },
            
            'access_security': {
                'priv_access_for_deploy': access_security.get('priv_access_for_deploy', app_data.get('priv_access_for_deploy', app_data.get('priv_access', 0) > 0)),
                'priv_access_reviewed_date': access_security.get('priv_access_reviewed_date', app_data.get('priv_access_reviewed_date', '')),
                'sast_enabled': access_security.get('sast_enabled', app_data.get('sast_enabled', False)),
                'priv_access_reviewed_stale': access_security.get('priv_access_reviewed_stale', False),
            },
            
            'compliance': {
                'release_page_url': compliance.get('release_page_url', app_data.get('release_page_url', '')),
                'compliance_evidence_page': compliance.get('compliance_evidence_page', app_data.get('compliance_evidence_page', '')),
            },
            
            'ai_adoption': {
                'copilot_enabled': ai_adoption.get('copilot_enabled', app_data.get('copilot_enabled', False)),
                'ai_tools_declared': ai_adoption.get('ai_tools_declared', app_data.get('ai_tools_declared', [])),
                'apis_published': ai_adoption.get('apis_published', app_data.get('apis_published', False)),
                'api_count': ai_adoption.get('api_count', app_data.get('api_count', 0)),
            },
            
            # Interview actions (if present in YAML)
            'improvement_action_1': app_data.get('improvement_action_1', ''),
            'improvement_action_2': app_data.get('improvement_action_2', ''),
            'improvement_action_3': app_data.get('improvement_action_3', ''),
        }
    
    def _build_score_dict(self, score_data: Dict) -> Dict:
        """Convert score data to format expected by recommendation engine"""
        # Map current DPI scores to mentor's pillar structure
        # Current: rf_score, flow_score, stability_score, automation_score
        # Mentor's: velocity, flow, stability, automation, ai_adoption
        
        return {
            'total_score': score_data.get('dpi', 0),
            
            # Create score object with pillar breakdown
            'score': {
                'velocity': score_data.get('rf_score', 0),  # RF maps to velocity
                'flow': score_data.get('flow_score', 0),
                'stability': score_data.get('stability_score', 0),
                'automation': score_data.get('automation_score', 0),
                'ai_adoption': 0,  # Not calculated yet in current system
            },
            
            # Also keep pillars format for compatibility
            'pillars': {
                'velocity': {'raw_score': score_data.get('rf_score', 0)},
                'flow': {'raw_score': score_data.get('flow_score', 0)},
                'stability': {'raw_score': score_data.get('stability_score', 0)},
                'automation': {'raw_score': score_data.get('automation_score', 0)},
                'ai_adoption': {'raw_score': 0},
            }
        }
    
    def _get_fallback_recommendations(self, app_data: Dict, score_data: Dict, max_recommendations: int) -> List[Dict]:
        """
        Provide simple fallback recommendations when engine is not available
        """
        recommendations = []
        dpi = score_data.get('dpi', 0)
        
        # Low DPI - focus on basics
        if dpi < 40:
            recommendations.append({
                'action': 'Enable CI automation',
                'detail': 'Set up continuous integration to automatically build and test your code. This is the foundation of DevOps automation.',
                'pillar': 'Automation',
                'effort': 'medium',
                'effort_emoji': '🔧',
                'points_gain': 10,
                'source': 'fallback'
            })
        
        # Check specific flags
        if not app_data.get('cd', False):
            recommendations.append({
                'action': 'Enable CD automation',
                'detail': 'Configure your deployment pipeline to trigger automatically after successful CI builds.',
                'pillar': 'Velocity',
                'effort': 'medium',
                'effort_emoji': '🔧',
                'points_gain': 8,
                'source': 'fallback'
            })
        
        if not app_data.get('rollback', False):
            recommendations.append({
                'action': 'Implement automated rollback',
                'detail': 'Configure your deployment pipeline to automatically rollback failed deployments.',
                'pillar': 'Stability',
                'effort': 'medium',
                'effort_emoji': '🔧',
                'points_gain': 6,
                'source': 'fallback'
            })
        
        # Medium DPI - push to advanced
        if 50 <= dpi < 70:
            recommendations.append({
                'action': 'Reduce approval gates',
                'detail': 'Streamline your deployment process by consolidating approvals into automated governance checks.',
                'pillar': 'Flow',
                'effort': 'high',
                'effort_emoji': '🏗',
                'points_gain': 6,
                'source': 'fallback'
            })
        
        # High DPI - reach elite
        if 70 <= dpi < 85:
            recommendations.append({
                'action': 'Achieve zero-touch deployment',
                'detail': 'Remove all manual intervention from your deployment process to reach Elite tier.',
                'pillar': 'Automation',
                'effort': 'high',
                'effort_emoji': '🏗',
                'points_gain': 10,
                'source': 'fallback'
            })
        
        return recommendations[:max_recommendations]


# Singleton instance
_recommendation_helper = None

def get_recommendation_helper() -> RecommendationHelper:
    """Get or create the recommendation helper singleton"""
    global _recommendation_helper
    if _recommendation_helper is None:
        _recommendation_helper = RecommendationHelper()
    return _recommendation_helper
