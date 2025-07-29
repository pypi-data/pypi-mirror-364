"""
Sensors module for sensor configuration and data.

This module provides classes for configuring and reading data from sensors.
"""

from instinct_py.device.sensors.manager import InstinctDeviceSensorsManager
from instinct_py.device.sensors.types import (
    SensorConfig,
    SensorData,
    SensorResponse,
)

__all__ = [
    "InstinctDeviceSensorsManager",
    "SensorConfig",
    "SensorData",
    "SensorResponse",
]
