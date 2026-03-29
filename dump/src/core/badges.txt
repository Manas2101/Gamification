"""
Badge Engine
============

Computes and assigns badges based on DevOps performance scores.

Badges are awarded across different categories:
    - Overall DPI badges (Platinum, Gold, Silver, Bronze)
    - Pillar-specific badges (Velocity Champion, Hygiene Hero, etc.)
    - Achievement badges (Improver, Consistent Performer, etc.)

Example:
    >>> from src.core.badges import BadgeEngine
    >>> engine = BadgeEngine()
    >>> badges = engine.compute_badges(scores_dict)

Author: DevOps Transformation Team
"""

import logging
from typing import Dict, List, Optional

# Configure module logger
logger = logging.getLogger(__name__)


class BadgeEngine:
    """
    Engine for computing and assigning performance badges.
    
    Badges provide gamification elements to encourage improvement
    and recognize high-performing teams.
    
    Attributes:
        TIER_THRESHOLDS (dict): Score thresholds for badge tiers
        PILLAR_BADGES (dict): Badge definitions for each pillar
        
    Example:
        >>> engine = BadgeEngine()
        >>> badges = engine.compute_badges({'dpi': 85, 'Release_Velocity_Score': 90})
    """
    
    # Badge tier thresholds
    TIER_THRESHOLDS = {
        'platinum': 95,
        'gold': 85,
        'silver': 70,
        'bronze': 50
    }
    
    # Pillar-specific badge definitions
    PILLAR_BADGES = {
        'Release_Velocity_Score': {
            'name': 'Velocity Champion',
            'icon': '🚀',
            'description': 'Excellence in release frequency and deployment speed'
        },
        'Git_Hygiene_Score': {
            'name': 'Hygiene Hero',
            'icon': '✨',
            'description': 'Maintaining clean and healthy repositories'
        },
        'Pipeline_Maturity_Score': {
            'name': 'Pipeline Pro',
            'icon': '⚙️',
            'description': 'Advanced CI/CD automation and practices'
        },
        'Compliance_Score': {
            'name': 'Compliance Champion',
            'icon': '📋',
            'description': 'Meeting all compliance and documentation requirements'
        },
        'Quality_Security_Score': {
            'name': 'Quality Guardian',
            'icon': '🛡️',
            'description': 'Strong quality and security practices'
        },
        'Adoption_Score': {
            'name': 'Innovation Leader',
            'icon': '💡',
            'description': 'Early adoption of modern tools and practices'
        }
    }
    
    # Overall DPI badges
    DPI_BADGES = {
        'platinum': {
            'name': 'DevOps Elite',
            'icon': '💎',
            'description': 'Top-tier DevOps maturity across all pillars'
        },
        'gold': {
            'name': 'DevOps Master',
            'icon': '🥇',
            'description': 'Excellent DevOps practices and performance'
        },
        'silver': {
            'name': 'DevOps Practitioner',
            'icon': '🥈',
            'description': 'Strong DevOps foundation with room to grow'
        },
        'bronze': {
            'name': 'DevOps Starter',
            'icon': '🥉',
            'description': 'Beginning the DevOps transformation journey'
        }
    }
    
    def __init__(self):
        """Initialize the badge engine."""
        logger.info("BadgeEngine initialized")
    
    def get_tier(self, score: float) -> Optional[str]:
        """
        Determine badge tier based on score.
        
        Args:
            score: Numeric score (0-100).
            
        Returns:
            Tier name ('platinum', 'gold', 'silver', 'bronze') or None.
        """
        if score is None:
            return None
        
        if score >= self.TIER_THRESHOLDS['platinum']:
            return 'platinum'
        elif score >= self.TIER_THRESHOLDS['gold']:
            return 'gold'
        elif score >= self.TIER_THRESHOLDS['silver']:
            return 'silver'
        elif score >= self.TIER_THRESHOLDS['bronze']:
            return 'bronze'
        
        return None
    
    def compute_dpi_badge(self, dpi_score: float) -> Optional[Dict]:
        """
        Compute overall DPI badge.
        
        Args:
            dpi_score: Overall DPI score (0-100).
            
        Returns:
            Badge dictionary with name, icon, tier, description.
            None if score doesn't qualify for a badge.
        """
        tier = self.get_tier(dpi_score)
        
        if tier and tier in self.DPI_BADGES:
            badge = self.DPI_BADGES[tier].copy()
            badge['tier'] = tier.capitalize()
            badge['score'] = dpi_score
            return badge
        
        return None
    
    def compute_pillar_badges(self, scores: Dict) -> List[Dict]:
        """
        Compute badges for individual pillars.
        
        Only awards badges for pillars with Gold or higher scores.
        
        Args:
            scores: Dictionary with pillar scores.
            
        Returns:
            List of badge dictionaries for qualifying pillars.
        """
        badges = []
        
        for pillar_key, badge_def in self.PILLAR_BADGES.items():
            score = scores.get(pillar_key)
            
            if score is None:
                continue
            
            tier = self.get_tier(score)
            
            # Only award pillar badges for gold or higher
            if tier in ['platinum', 'gold']:
                badge = badge_def.copy()
                badge['tier'] = tier.capitalize()
                badge['score'] = score
                badge['pillar'] = pillar_key
                badges.append(badge)
        
        return badges
    
    def compute_achievement_badges(
        self, 
        current_scores: Dict, 
        previous_scores: Dict = None
    ) -> List[Dict]:
        """
        Compute achievement badges based on progress.
        
        Achievement badges reward improvement and consistency.
        
        Args:
            current_scores: Current period scores.
            previous_scores: Previous period scores (optional).
            
        Returns:
            List of achievement badge dictionaries.
        """
        badges = []
        
        # Check for improvement badge
        if previous_scores:
            current_dpi = current_scores.get('dpi', 0)
            previous_dpi = previous_scores.get('dpi', 0)
            
            improvement = current_dpi - previous_dpi
            
            if improvement >= 10:
                badges.append({
                    'name': 'Rapid Improver',
                    'icon': '📈',
                    'description': f'Improved DPI by {improvement:.1f} points',
                    'tier': 'Achievement',
                    'improvement': improvement
                })
            elif improvement >= 5:
                badges.append({
                    'name': 'Steady Climber',
                    'icon': '🔼',
                    'description': f'Improved DPI by {improvement:.1f} points',
                    'tier': 'Achievement',
                    'improvement': improvement
                })
        
        # Check for consistency badge (all pillars above threshold)
        pillar_scores = [
            current_scores.get('Release_Velocity_Score', 0),
            current_scores.get('Git_Hygiene_Score', 0),
            current_scores.get('Pipeline_Maturity_Score', 0),
            current_scores.get('Compliance_Score', 0),
            current_scores.get('Quality_Security_Score', 0),
            current_scores.get('Adoption_Score', 0)
        ]
        
        if all(score >= 70 for score in pillar_scores):
            badges.append({
                'name': 'Well Rounded',
                'icon': '🎯',
                'description': 'Strong performance across all pillars',
                'tier': 'Achievement'
            })
        
        # Check for perfect pillar badge
        perfect_pillars = sum(1 for score in pillar_scores if score >= 95)
        if perfect_pillars >= 3:
            badges.append({
                'name': 'Excellence Achiever',
                'icon': '⭐',
                'description': f'Achieved excellence in {perfect_pillars} pillars',
                'tier': 'Achievement'
            })
        
        return badges
    
    def compute_badges(
        self, 
        scores: Dict, 
        previous_scores: Dict = None
    ) -> List[Dict]:
        """
        Compute all applicable badges for a team.
        
        This is the main entry point for badge computation.
        
        Args:
            scores: Dictionary with all pillar scores and DPI.
            previous_scores: Previous period scores for achievement badges.
            
        Returns:
            List of all earned badge dictionaries.
        """
        all_badges = []
        
        # Overall DPI badge
        dpi_badge = self.compute_dpi_badge(scores.get('dpi', 0))
        if dpi_badge:
            all_badges.append(dpi_badge)
        
        # Pillar-specific badges
        pillar_badges = self.compute_pillar_badges(scores)
        all_badges.extend(pillar_badges)
        
        # Achievement badges
        achievement_badges = self.compute_achievement_badges(scores, previous_scores)
        all_badges.extend(achievement_badges)
        
        logger.debug(f"Computed {len(all_badges)} badges")
        return all_badges
    
    def format_badges_display(self, badges: List[Dict]) -> str:
        """
        Format badges for display.
        
        Args:
            badges: List of badge dictionaries.
            
        Returns:
            Formatted string for display.
        """
        if not badges:
            return "No badges earned yet"
        
        lines = []
        for badge in badges:
            icon = badge.get('icon', '🏅')
            name = badge.get('name', 'Badge')
            tier = badge.get('tier', '')
            lines.append(f"{icon} {name} ({tier})")
        
        return " | ".join(lines)


def compute_badges(row: Dict) -> List[str]:
    """
    Convenience function for computing badges from a data row.
    
    Compatible with pandas DataFrame apply operations.
    
    Args:
        row: Dictionary or Series with score columns.
        
    Returns:
        List of badge name strings.
    """
    engine = BadgeEngine()
    badges = engine.compute_badges(dict(row))
    return [badge.get('name', '') for badge in badges]


def get_badge_tier(score: float) -> Optional[str]:
    """
    Convenience function to get badge tier for a score.
    
    Args:
        score: Numeric score (0-100).
        
    Returns:
        Tier name or None.
    """
    engine = BadgeEngine()
    tier = engine.get_tier(score)
    return tier.capitalize() if tier else None
