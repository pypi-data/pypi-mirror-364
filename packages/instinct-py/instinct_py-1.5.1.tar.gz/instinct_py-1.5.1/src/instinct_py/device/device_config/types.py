"""
Type definitions for the device configuration subsystem.

This module defines the data models used for storing and retrieving
configuration data on the device.
"""

from typing import Any, Optional

import uuid
from pydantic import BaseModel


class DeviceConfig(BaseModel):
    """Device configuration entry.

    Represents a configuration item stored on the device.

    Parameters
    ----------
    key : str
        Unique identifier for the configuration
    value : Any
        Value to store (will be serialized to string)
    id : Optional[str], optional
        Unique ID (auto-generated if not provided), by default None
    expires_in : Optional[str], optional
        Time-to-live (e.g., "1h", "2d", "30m"), by default None
    expires_on : Optional[str], optional
        Expiration date (ISO 8601 format), by default None
    created_at : Optional[str], optional
        Creation timestamp, by default None
    updated_at : Optional[str], optional
        Last update timestamp, by default None
    """

    key: str
    value: Any
    id: Optional[str] = None
    expires_in: Optional[str] = None
    expires_on: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __init__(self, **data: Any) -> None:
        """Initialize a device configuration entry.

        Generates a UUID if id is not provided.
        """
        if "id" not in data or data["id"] is None:
            data["id"] = str(uuid.uuid4())
        super().__init__(**data)

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True


class DeviceConfigResponse(BaseModel):
    """Response from device configuration operations.

    Parameters
    ----------
    message : str
        Operation result message
    success : bool
        Whether the operation was successful
    config : Optional[DeviceConfig], optional
        The configuration data if applicable, by default None
    """

    message: str
    success: bool
    config: Optional[DeviceConfig] = None
