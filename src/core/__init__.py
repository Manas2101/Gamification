"""
Core Module
===========

Core business logic for DevOps metrics and scoring.

Classes:
    - MetricsCalculator: Calculates 6-pillar DPI scores
    - BadgeEngine: Computes badges based on scores
    - RecommendationEngine: Generates improvement recommendations
"""

from src.core.calculator import MetricsCalculator
from src.core.badges import BadgeEngine
from src.core.recommendations import RecommendationEngine

__all__ = ["MetricsCalculator", "BadgeEngine", "RecommendationEngine"]
