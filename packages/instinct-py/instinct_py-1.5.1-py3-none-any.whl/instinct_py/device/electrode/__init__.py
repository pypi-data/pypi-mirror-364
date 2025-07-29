"""
Electrode module for electrode configuration and data.

This module provides classes for configuring and reading data from electrodes.
"""

from instinct_py.device.electrode.manager import InstinctDeviceElectrodesManager
from instinct_py.device.electrode.types import (
    ElectrodeConfig,
    ElectrodeData,
    ElectrodeResponse,
)

__all__ = [
    "InstinctDeviceElectrodesManager",
    "ElectrodeConfig",
    "ElectrodeData",
    "ElectrodeResponse",
]
