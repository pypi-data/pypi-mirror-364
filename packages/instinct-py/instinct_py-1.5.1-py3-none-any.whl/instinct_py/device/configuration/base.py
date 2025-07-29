"""
Configuration module for Instinct Device API URLs.

This module provides configuration classes for managing API URLs and endpoints.
"""

from typing import Optional


class InstinctDeviceBaseConfiguration:
    """Base configuration for all device services.

    Parameters
    ----------
    base_url : Optional[str], optional
        Base URL for API requests, by default None
    system_base : Optional[str], optional
        Base URL for system API endpoints, by default None
    streams_base : Optional[str], optional
        Base URL for streams API endpoints, by default None
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        system_base: Optional[str] = None,
        streams_base: Optional[str] = None,
    ) -> None:
        """Initialize the base configuration with the provided URLs or defaults."""
        self.base_url = base_url or "http://localhost:42069"
        self.system_base = system_base or f"{self.base_url}/system"
        self.streams_base = streams_base or f"{self.base_url}/streams"


class InstinctDeviceSystemConfiguration:
    """System-specific configuration for Instinct Device API endpoints.

    Parameters
    ----------
    base_configuration : InstinctDeviceBaseConfiguration
        Base configuration for API URLs
    """

    def __init__(self, base_configuration: InstinctDeviceBaseConfiguration) -> None:
        """Initialize system configuration with the provided base configuration."""
        self.base_configuration = base_configuration
        system_base = self.base_configuration.system_base

        # Define system API endpoints
        self.url_device_get_state = f"{system_base}/healthz"
        self.url_device_get_name = f"{system_base}/system/hostname"
        self.url_device_set_name = f"{system_base}/system/hostname"
        self.url_device_send_debug_command = f"{system_base}/system/debug"


class InstinctDeviceStreamsConfiguration:
    """Streams-specific configuration for device API endpoints.

    Parameters
    ----------
    base_configuration : InstinctDeviceBaseConfiguration
        Base configuration for API URLs
    """

    def __init__(self, base_configuration: InstinctDeviceBaseConfiguration) -> None:
        """Initialize streams configuration with the provided base configuration."""
        self.base_configuration = base_configuration
        streams_base = self.base_configuration.streams_base

        # Define streams API endpoints
        self.url_stream_create = f"{streams_base}/stream"
        self.url_stream_get = f"{streams_base}/stream"
        self.url_stream_delete = f"{streams_base}/stream"
        self.url_stream_start = f"{streams_base}/stream/start"
        self.url_stream_stop = f"{streams_base}/stream/stop"
        self.url_stream_signal = f"{streams_base}/stream/signal"
        self.url_stream_reconcile = f"{streams_base}/stream/reconcile"

        # Node operations
        self.url_node_create = f"{streams_base}/node"
        self.url_node_get = f"{streams_base}/node"
        self.url_node_delete = f"{streams_base}/node"
        self.url_node_signal = f"{streams_base}/node/signal"

        # Pipe operations
        self.url_pipe_create = f"{streams_base}/pipe"
        self.url_pipe_get = f"{streams_base}/pipe"
        self.url_pipe_delete = f"{streams_base}/pipe"
