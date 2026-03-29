"""
API Module
==========

External API clients for data collection and integration.

Classes:
    - DataSightClient: Client for DataSight metrics API (MTTR, LTTD, RF, CFR)
    - GitHubClient: Client for GitHub API (hygiene checks, repo analysis)
    - LLMClient: Client for LLM Gateway (documentation generation)
"""

from src.api.datasight import DataSightClient
from src.api.github import GitHubClient
from src.api.llm import LLMClient

__all__ = ["DataSightClient", "GitHubClient", "LLMClient"]
