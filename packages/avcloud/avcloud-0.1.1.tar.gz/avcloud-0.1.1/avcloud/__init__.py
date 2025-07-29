"""
AVCloud SDK

A Python SDK for interfacing with AVCloud services.
"""

__version__ = "0.0.1"
__author__ = "Summer Li"
__email__ = "jiaoyli@umich.edu"

# Import main components
from .experimental.client import AvCloudClient

__all__ = [
    "__version__",
    "AvCloudClient",
]
