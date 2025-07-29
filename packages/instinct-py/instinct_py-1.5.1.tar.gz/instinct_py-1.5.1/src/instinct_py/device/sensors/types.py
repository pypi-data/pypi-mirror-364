"""
Type definitions for the sensors subsystem.

This module defines the data models used for sensor data and configuration.
"""

from typing import Optional

from pydantic import BaseModel


class SensorConfig(BaseModel):
    """Configuration for a sensor.

    Parameters
    ----------
    type : str
        Type of the sensor (e.g., "accelerometer", "gyroscope")
    enabled : bool
        Whether the sensor is enabled
    sample_rate : Optional[int], optional
        Sample rate in Hz, by default None
    range : Optional[float], optional
        Measurement range, by default None
    """

    type: str
    enabled: bool
    sample_rate: Optional[int] = None
    range: Optional[float] = None


class SensorData(BaseModel):
    """Data from a sensor.

    Parameters
    ----------
    type : str
        Type of the sensor
    x : float
        X-axis value
    y : float
        Y-axis value
    z : float
        Z-axis value
    timestamp : float
        Timestamp of the reading in seconds
    """

    type: str
    x: float
    y: float
    z: float
    timestamp: float


class SensorResponse(BaseModel):
    """Response from sensor operations.

    Parameters
    ----------
    message : str
        Response message
    success : bool
        Whether the operation was successful
    sensor : Optional[SensorConfig], optional
        Sensor configuration if applicable, by default None
    """

    message: str
    success: bool
    sensor: Optional[SensorConfig] = None
