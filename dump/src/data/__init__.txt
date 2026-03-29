"""
Data Module
===========

Data layer for database operations and registry loading.

Classes:
    - Database: SQLite database operations for metrics storage
    - RegistryLoader: YAML application registry loader
"""

from src.data.database import Database
from src.data.registry import RegistryLoader

__all__ = ["Database", "RegistryLoader"]
