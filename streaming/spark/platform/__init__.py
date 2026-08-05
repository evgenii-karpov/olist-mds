"""Shared lakehouse platform contracts.

This package intentionally contains infrastructure and table definitions only.
Entity decoding and business normalization belong to the entity packages.
"""

from .config import SparkPlatformConfig
from .topology import BRONZE_QUERY, SILVER_QUERIES, checkpoint_path

__all__ = [
    "BRONZE_QUERY",
    "SILVER_QUERIES",
    "SparkPlatformConfig",
    "checkpoint_path",
]
