"""
Device configuration manager module.

This module provides the DeviceConfigManager class for storing and retrieving
persistent configuration values on the device.
"""

from typing import Any, Dict, List, Union

from instinct_py.device.configuration.base import InstinctDeviceSystemConfiguration
from instinct_py.device.device_config.types import (
    DeviceConfig,
    DeviceConfigResponse,
)
from instinct_py.utils.http_client import HttpClient


class InstinctDeviceConfigManager:
    """Manages device configuration storage.

    Provides methods for creating, retrieving, updating, and deleting
    configuration entries on the device.

    Parameters
    ----------
    device : Any
        The parent InstinctDevice instance
    """

    def __init__(self, device: Any) -> None:
        """Initialize the device configuration manager.

        Parameters
        ----------
        device : Any
            The parent InstinctDevice instance
        """
        self._device = device
        self._http_client = HttpClient()
        self._system_configuration = InstinctDeviceSystemConfiguration(
            device.base_configuration
        )
        self._device_config_base_url = (
            f"{self._system_configuration.base_configuration.system_base}/config"
        )

    def create_config(
        self, config_data: Union[Dict[str, Any], DeviceConfig]
    ) -> DeviceConfig:
        """Create a new configuration entry.

        Parameters
        ----------
        config_data : Union[Dict[str, Any], DeviceConfig]
            The configuration data to store

        Returns
        -------
        DeviceConfig
            The created configuration entry

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # Store user preferences
        >>> config = device.device_config_manager.create_config({
        ...     "key": "userPreference.theme",
        ...     "value": "dark"
        ... })
        >>>
        >>> # Store temporary data with expiration
        >>> config = device.device_config_manager.create_config({
        ...     "key": "session.authToken",
        ...     "value": "abc123xyz",
        ...     "expires_in": "1h"
        ... })
        """
        # Convert to DeviceConfig if it's a dict
        if isinstance(config_data, dict):
            config = DeviceConfig(**config_data)
        else:
            config = config_data

        try:
            response = self._http_client.post(
                self._device_config_base_url,
                json=config.model_dump(),
            )
            return DeviceConfig.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't create configuration. {error}")

    def get_config(self, key: str) -> DeviceConfig:
        """Retrieve a configuration by key.

        Parameters
        ----------
        key : str
            The key of the configuration to retrieve

        Returns
        -------
        DeviceConfig
            The retrieved configuration entry

        Raises
        ------
        Exception
            If the request fails or the configuration doesn't exist

        Examples
        --------
        >>> # Retrieve a configuration
        >>> config = device.device_config_manager.get_config("userPreference.theme")
        >>> print(f"Theme preference: {config.value}")
        """
        try:
            response = self._http_client.get(
                f"{self._device_config_base_url}/{key}",
            )
            return DeviceConfig.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't get configuration for key '{key}'. {error}")

    def list_configs(self) -> List[DeviceConfig]:
        """List all configurations.

        Returns
        -------
        List[DeviceConfig]
            All configuration entries

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # List all configurations
        >>> configs = device.device_config_manager.list_configs()
        >>> for config in configs:
        ...     print(f"{config.key}: {config.value}")
        """
        try:
            response = self._http_client.get(self._device_config_base_url)
            return [DeviceConfig.model_validate(item) for item in response]
        except Exception as error:
            raise Exception(f"Couldn't list configurations. {error}")

    def update_config(
        self, key: str, config_data: Union[Dict[str, Any], DeviceConfig]
    ) -> DeviceConfig:
        """Update an existing configuration.

        Parameters
        ----------
        key : str
            The key of the configuration to update
        config_data : Union[Dict[str, Any], DeviceConfig]
            The new configuration data

        Returns
        -------
        DeviceConfig
            The updated configuration entry

        Raises
        ------
        Exception
            If the request fails or the configuration doesn't exist

        Examples
        --------
        >>> # Update a configuration
        >>> updated_config = device.device_config_manager.update_config(
        ...     "userPreference.theme",
        ...     {
        ...         "key": "userPreference.theme",
        ...         "value": "light"
        ...     }
        ... )
        """
        # Convert to DeviceConfig if it's a dict
        if isinstance(config_data, dict):
            config = DeviceConfig(**config_data)
        else:
            config = config_data

        try:
            response = self._http_client.put(
                f"{self._device_config_base_url}/{key}",
                json=config.model_dump(),
            )
            return DeviceConfig.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't update configuration for key '{key}'. {error}")

    def delete_config(self, key: str) -> DeviceConfigResponse:
        """Delete a configuration entry.

        Parameters
        ----------
        key : str
            The key of the configuration to delete

        Returns
        -------
        DeviceConfigResponse
            Response from the delete operation

        Raises
        ------
        Exception
            If the request fails or the configuration doesn't exist

        Examples
        --------
        >>> # Delete a configuration
        >>> response = device.device_config_manager.delete_config("session.authToken")
        >>> if response.success:
        ...     print("Configuration deleted successfully")
        """
        try:
            response = self._http_client.delete(
                f"{self._device_config_base_url}/{key}",
            )
            return DeviceConfigResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't delete configuration for key '{key}'. {error}")
