"""
Configuration module for Instinct device API URLs.

This module exports configuration classes for managing API URLs and endpoints.
"""

from instinct_py.device.configuration.base import (
    InstinctDeviceBaseConfiguration,
    InstinctDeviceStreamsConfiguration,
    InstinctDeviceSystemConfiguration,
)

__all__ = [
    "InstinctDeviceBaseConfiguration",
    "InstinctDeviceStreamsConfiguration",
    "InstinctDeviceSystemConfiguration",
]
