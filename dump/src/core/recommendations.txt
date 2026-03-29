"""
Recommendation Engine
=====================

Generates actionable improvement recommendations based on DevOps scores.

Analyzes pillar scores and provides targeted suggestions for improvement,
prioritized by impact and effort required.

Example:
    >>> from src.core.recommendations import RecommendationEngine
    >>> engine = RecommendationEngine()
    >>> recs = engine.generate_recommendations(scores_dict)

Author: DevOps Transformation Team
"""

import logging
from typing import Dict, List, Optional

# Configure module logger
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Engine for generating improvement recommendations.
    
    Analyzes scores across all pillars and generates prioritized
    recommendations based on current performance gaps.
    
    Attributes:
        IMPROVEMENT_THRESHOLD (int): Score below which improvements are suggested
        PRIORITY_WEIGHTS (dict): Weights for prioritizing recommendations
        
    Example:
        >>> engine = RecommendationEngine()
        >>> recs = engine.generate_recommendations({'dpi': 65, ...})
    """
    
    # Score threshold for generating recommendations
    IMPROVEMENT_THRESHOLD = 80
    
    # Recommendation templates by pillar
    RECOMMENDATIONS = {
        'Release_Velocity_Score': [
            {
                'threshold': 50,
                'priority': 'high',
                'title': 'Increase Release Frequency',
                'description': 'Aim for more frequent, smaller releases to reduce risk and improve feedback loops.',
                'actions': [
                    'Break down large features into smaller increments',
                    'Implement feature flags for gradual rollouts',
                    'Automate release processes to reduce manual effort'
                ],
                'impact': 'High',
                'effort': 'Medium'
            },
            {
                'threshold': 70,
                'priority': 'medium',
                'title': 'Reduce Lead Time to Deploy',
                'description': 'Optimize your deployment pipeline to reduce time from commit to production.',
                'actions': [
                    'Identify and eliminate pipeline bottlenecks',
                    'Parallelize test execution where possible',
                    'Implement automated deployment approvals'
                ],
                'impact': 'High',
                'effort': 'Medium'
            },
            {
                'threshold': 85,
                'priority': 'low',
                'title': 'Achieve Zero-Touch Deployments',
                'description': 'Fully automate deployments to eliminate manual intervention.',
                'actions': [
                    'Implement automated rollback mechanisms',
                    'Add comprehensive deployment health checks',
                    'Enable self-service deployments for teams'
                ],
                'impact': 'Medium',
                'effort': 'High'
            }
        ],
        'Git_Hygiene_Score': [
            {
                'threshold': 50,
                'priority': 'high',
                'title': 'Clean Up Stale Branches',
                'description': 'Remove branches that are no longer active to maintain repository health.',
                'actions': [
                    'Delete merged branches automatically',
                    'Set up branch protection rules',
                    'Establish branch naming conventions'
                ],
                'impact': 'Medium',
                'effort': 'Low'
            },
            {
                'threshold': 70,
                'priority': 'medium',
                'title': 'Improve PR Review Process',
                'description': 'Ensure PRs are reviewed promptly to maintain code quality.',
                'actions': [
                    'Set up PR review reminders',
                    'Define maximum PR size guidelines',
                    'Implement automated code review tools'
                ],
                'impact': 'High',
                'effort': 'Low'
            },
            {
                'threshold': 85,
                'priority': 'low',
                'title': 'Optimize PR Size',
                'description': 'Keep PRs small and focused for easier review and faster merging.',
                'actions': [
                    'Break large changes into smaller PRs',
                    'Use draft PRs for work in progress',
                    'Implement PR templates for consistency'
                ],
                'impact': 'Medium',
                'effort': 'Low'
            }
        ],
        'Pipeline_Maturity_Score': [
            {
                'threshold': 40,
                'priority': 'high',
                'title': 'Implement CI/CD Pipeline',
                'description': 'Set up automated build and deployment pipelines.',
                'actions': [
                    'Configure automated builds on commit',
                    'Add automated testing to pipeline',
                    'Implement deployment automation'
                ],
                'impact': 'High',
                'effort': 'High'
            },
            {
                'threshold': 60,
                'priority': 'medium',
                'title': 'Add Automated Rollback',
                'description': 'Implement automatic rollback capabilities for failed deployments.',
                'actions': [
                    'Define rollback triggers and criteria',
                    'Implement health check monitoring',
                    'Test rollback procedures regularly'
                ],
                'impact': 'High',
                'effort': 'Medium'
            },
            {
                'threshold': 80,
                'priority': 'low',
                'title': 'Standardize Pipeline Templates',
                'description': 'Use standardized pipeline templates across projects.',
                'actions': [
                    'Create reusable pipeline templates',
                    'Document pipeline best practices',
                    'Implement pipeline as code'
                ],
                'impact': 'Medium',
                'effort': 'Medium'
            }
        ],
        'Compliance_Score': [
            {
                'threshold': 50,
                'priority': 'high',
                'title': 'Document Release Process',
                'description': 'Create and maintain release documentation.',
                'actions': [
                    'Set up release page with deployment history',
                    'Document rollback procedures',
                    'Maintain change log'
                ],
                'impact': 'Medium',
                'effort': 'Low'
            },
            {
                'threshold': 75,
                'priority': 'medium',
                'title': 'Review Privileged Access',
                'description': 'Ensure privileged access reviews are current.',
                'actions': [
                    'Conduct quarterly access reviews',
                    'Implement least privilege principle',
                    'Document access control policies'
                ],
                'impact': 'High',
                'effort': 'Medium'
            },
            {
                'threshold': 90,
                'priority': 'low',
                'title': 'Automate CR Creation',
                'description': 'Automate change request creation for deployments.',
                'actions': [
                    'Integrate CR system with deployment pipeline',
                    'Auto-populate CR details from commits',
                    'Implement approval workflows'
                ],
                'impact': 'Medium',
                'effort': 'Medium'
            }
        ],
        'Quality_Security_Score': [
            {
                'threshold': 35,
                'priority': 'high',
                'title': 'Enable SAST Scanning',
                'description': 'Implement Static Application Security Testing.',
                'actions': [
                    'Configure SAST tool in pipeline',
                    'Define security policy rules',
                    'Train team on security best practices'
                ],
                'impact': 'High',
                'effort': 'Medium'
            },
            {
                'threshold': 70,
                'priority': 'medium',
                'title': 'Integrate SonarQube',
                'description': 'Set up code quality analysis with SonarQube.',
                'actions': [
                    'Configure SonarQube project',
                    'Define quality gates',
                    'Add SonarQube to CI pipeline'
                ],
                'impact': 'High',
                'effort': 'Low'
            },
            {
                'threshold': 85,
                'priority': 'low',
                'title': 'Define Data Classification',
                'description': 'Classify data handled by the application.',
                'actions': [
                    'Identify data types processed',
                    'Apply appropriate classification labels',
                    'Implement data handling procedures'
                ],
                'impact': 'Medium',
                'effort': 'Low'
            }
        ],
        'Adoption_Score': [
            {
                'threshold': 30,
                'priority': 'high',
                'title': 'Enable GitHub Copilot',
                'description': 'Adopt AI-assisted coding tools to improve productivity.',
                'actions': [
                    'Request Copilot licenses for team',
                    'Provide training on effective usage',
                    'Share best practices and tips'
                ],
                'impact': 'Medium',
                'effort': 'Low'
            },
            {
                'threshold': 50,
                'priority': 'medium',
                'title': 'Declare AI Tools Usage',
                'description': 'Document AI tools used in development process.',
                'actions': [
                    'Inventory AI tools in use',
                    'Document usage guidelines',
                    'Ensure compliance with policies'
                ],
                'impact': 'Low',
                'effort': 'Low'
            },
            {
                'threshold': 75,
                'priority': 'low',
                'title': 'Publish APIs',
                'description': 'Expose and document APIs for reuse.',
                'actions': [
                    'Identify reusable APIs',
                    'Create API documentation',
                    'Register in API catalog'
                ],
                'impact': 'Medium',
                'effort': 'Medium'
            }
        ]
    }
    
    def __init__(self):
        """Initialize the recommendation engine."""
        logger.info("RecommendationEngine initialized")
    
    def _get_pillar_recommendations(
        self, 
        pillar: str, 
        score: float
    ) -> List[Dict]:
        """
        Get recommendations for a specific pillar.
        
        Args:
            pillar: Pillar name (e.g., 'Release_Velocity_Score').
            score: Current pillar score.
            
        Returns:
            List of applicable recommendation dictionaries.
        """
        if pillar not in self.RECOMMENDATIONS:
            return []
        
        applicable = []
        for rec in self.RECOMMENDATIONS[pillar]:
            if score < rec['threshold']:
                rec_copy = rec.copy()
                rec_copy['pillar'] = pillar
                rec_copy['current_score'] = score
                rec_copy['gap'] = rec['threshold'] - score
                applicable.append(rec_copy)
        
        return applicable
    
    def generate_recommendations(
        self, 
        scores: Dict, 
        max_recommendations: int = 5
    ) -> List[Dict]:
        """
        Generate prioritized recommendations based on scores.
        
        Args:
            scores: Dictionary with all pillar scores.
            max_recommendations: Maximum number of recommendations to return.
            
        Returns:
            List of recommendation dictionaries, sorted by priority.
        """
        all_recommendations = []
        
        # Collect recommendations from all pillars
        pillar_keys = [
            'Release_Velocity_Score',
            'Git_Hygiene_Score',
            'Pipeline_Maturity_Score',
            'Compliance_Score',
            'Quality_Security_Score',
            'Adoption_Score'
        ]
        
        for pillar in pillar_keys:
            score = scores.get(pillar, 0)
            if score < self.IMPROVEMENT_THRESHOLD:
                recs = self._get_pillar_recommendations(pillar, score)
                all_recommendations.extend(recs)
        
        # Sort by priority and gap
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_recommendations.sort(
            key=lambda x: (priority_order.get(x['priority'], 3), -x.get('gap', 0))
        )
        
        # Return top recommendations
        result = all_recommendations[:max_recommendations]
        logger.debug(f"Generated {len(result)} recommendations")
        return result
    
    def format_recommendations(self, recommendations: List[Dict]) -> str:
        """
        Format recommendations for display.
        
        Args:
            recommendations: List of recommendation dictionaries.
            
        Returns:
            Formatted string for display.
        """
        if not recommendations:
            return "🎉 Great job! No critical improvements needed."
        
        lines = []
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(
                rec['priority'], '⚪'
            )
            
            lines.append(f"\n### {i}. {rec['title']} {priority_icon}")
            lines.append(f"**Priority**: {rec['priority'].capitalize()}")
            lines.append(f"**Impact**: {rec['impact']} | **Effort**: {rec['effort']}")
            lines.append(f"\n{rec['description']}")
            lines.append("\n**Actions:**")
            for action in rec.get('actions', []):
                lines.append(f"- {action}")
        
        return "\n".join(lines)
    
    def get_quick_wins(self, scores: Dict) -> List[Dict]:
        """
        Get quick win recommendations (high impact, low effort).
        
        Args:
            scores: Dictionary with all pillar scores.
            
        Returns:
            List of quick win recommendations.
        """
        all_recs = self.generate_recommendations(scores, max_recommendations=20)
        
        quick_wins = [
            rec for rec in all_recs
            if rec.get('impact') == 'High' and rec.get('effort') == 'Low'
        ]
        
        return quick_wins[:3]
