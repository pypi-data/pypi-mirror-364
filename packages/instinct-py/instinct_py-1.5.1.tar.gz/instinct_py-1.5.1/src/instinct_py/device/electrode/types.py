"""
Type definitions for the electrode subsystem.

This module defines the data models used for electrode data and configuration.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class ElectrodeConfig(BaseModel):
    """Configuration for an electrode.

    Parameters
    ----------
    position : str
        Standard 10-20 position of the electrode
    enabled : bool
        Whether the electrode is enabled
    gain : Optional[float], optional
        Gain value for the electrode, by default None
    """

    position: str
    enabled: bool
    gain: Optional[float] = None


class ElectrodeData(BaseModel):
    """Data from an electrode.

    Parameters
    ----------
    position : str
        Standard 10-20 position of the electrode
    value : float
        Value read from the electrode
    timestamp : float
        Timestamp of the reading in seconds
    """

    position: str
    value: float
    timestamp: float


class ElectrodeResponse(BaseModel):
    """Response from electrode operations.

    Parameters
    ----------
    message : str
        Response message
    success : bool
        Whether the operation was successful
    electrode : Optional[ElectrodeConfig], optional
        Electrode configuration if applicable, by default None
    """

    message: str
    success: bool
    electrode: Optional[ElectrodeConfig] = None
