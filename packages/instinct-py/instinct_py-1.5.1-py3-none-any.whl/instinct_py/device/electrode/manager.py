"""
Electrode manager module.

This module provides the InstinctDeviceElectrodesManager class for managing
electrode configurations on the device.
"""

from typing import Any, Dict, List, Optional, Union

from instinct_py.device.electrode.types import ElectrodeConfig, ElectrodeResponse
from instinct_py.utils.http_client import HttpClient


class InstinctDeviceElectrodesManager:
    """Manager for electrode configuration and data.

    Provides methods for configuring and reading data from electrodes.

    Parameters
    ----------
    device : Any
        The parent InstinctDevice instance
    positions : List[str]
        List of available electrode positions
    """

    def __init__(self, device: Any, positions: List[str]) -> None:
        """Initialize the electrode manager.

        Parameters
        ----------
        device : Any
            The parent InstinctDevice instance
        positions : List[str]
            List of available electrode positions
        """
        self._device = device
        self._http_client = HttpClient()
        self._positions = positions
        self._electrode_base_url = f"{device.base_configuration.system_base}/electrodes"

    @property
    def positions(self) -> List[str]:
        """Get the available electrode positions.

        Returns
        -------
        List[str]
            List of available electrode positions
        """
        return self._positions

    async def get_electrode(
        self, position: str, timeout: int = 1000
    ) -> ElectrodeConfig:
        """Get configuration for a specific electrode.

        Parameters
        ----------
        position : str
            Position of the electrode (e.g., "PZ", "O1", "O2")
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        ElectrodeConfig
            Configuration for the electrode

        Raises
        ------
        ValueError
            If the position is not valid
        Exception
            If the request fails

        Examples
        --------
        >>> # Get configuration for the PZ electrode
        >>> electrode = await device.electrode_manager.get_electrode("PZ")
        >>> print(f"PZ electrode enabled: {electrode.enabled}")
        """
        if position not in self._positions:
            raise ValueError(f"Invalid electrode position: {position}")

        try:
            response = self._http_client.get(
                f"{self._electrode_base_url}/{position}",
                timeout=timeout / 1000,
            )
            return ElectrodeConfig.model_validate(response)
        except Exception as error:
            raise Exception(
                f"Couldn't get electrode configuration for {position}. {error}"
            )

    async def set_electrode(
        self,
        position: str,
        config: Union[Dict[str, Any], ElectrodeConfig],
        timeout: int = 1000,
    ) -> ElectrodeResponse:
        """Configure a specific electrode.

        Parameters
        ----------
        position : str
            Position of the electrode (e.g., "PZ", "O1", "O2")
        config : Union[Dict[str, Any], ElectrodeConfig]
            Configuration for the electrode
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        ElectrodeResponse
            Response from the configuration operation

        Raises
        ------
        ValueError
            If the position is not valid
        Exception
            If the request fails

        Examples
        --------
        >>> # Enable the PZ electrode with gain of 1.0
        >>> response = await device.electrode_manager.set_electrode(
        ...     "PZ",
        ...     {
        ...         "position": "PZ",
        ...         "enabled": True,
        ...         "gain": 1.0,
        ...     }
        ... )
        >>> if response.success:
        ...     print("Electrode configured successfully")
        """
        if position not in self._positions:
            raise ValueError(f"Invalid electrode position: {position}")

        # Convert to ElectrodeConfig if it's a dict
        if isinstance(config, dict):
            electrode_config = ElectrodeConfig(**config)
        else:
            electrode_config = config

        # Ensure position in config matches the requested position
        if electrode_config.position != position:
            raise ValueError(
                f"Position mismatch: {position} vs {electrode_config.position}"
            )

        try:
            response = self._http_client.patch(
                f"{self._electrode_base_url}/{position}",
                json=electrode_config.model_dump(),
                timeout=timeout / 1000,
            )
            return ElectrodeResponse.model_validate(response)
        except Exception as error:
            raise Exception(
                f"Couldn't set electrode configuration for {position}. {error}"
            )

    async def list_electrodes(self, timeout: int = 1000) -> List[ElectrodeConfig]:
        """List configurations for all electrodes.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        List[ElectrodeConfig]
            List of electrode configurations

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # List all electrode configurations
        >>> electrodes = await device.electrode_manager.list_electrodes()
        >>> for electrode in electrodes:
        ...     print(f"{electrode.position}: {'enabled' if electrode.enabled else 'disabled'}")
        """
        try:
            response = self._http_client.get(
                self._electrode_base_url,
                timeout=timeout / 1000,
            )
            return [ElectrodeConfig.model_validate(item) for item in response]
        except Exception as error:
            raise Exception(f"Couldn't list electrode configurations. {error}")

    async def enable_electrode(
        self, position: str, gain: Optional[float] = None, timeout: int = 1000
    ) -> ElectrodeResponse:
        """Enable a specific electrode.

        Parameters
        ----------
        position : str
            Position of the electrode (e.g., "PZ", "O1", "O2")
        gain : Optional[float], optional
            Gain value for the electrode, by default None
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        ElectrodeResponse
            Response from the enable operation

        Raises
        ------
        ValueError
            If the position is not valid
        Exception
            If the request fails

        Examples
        --------
        >>> # Enable the PZ electrode
        >>> response = await device.electrode_manager.enable_electrode("PZ")
        >>> if response.success:
        ...     print("Electrode enabled successfully")
        """
        if position not in self._positions:
            raise ValueError(f"Invalid electrode position: {position}")

        try:
            # Get current configuration
            current_config = await self.get_electrode(position, timeout)

            # Update configuration
            current_config.enabled = True
            if gain is not None:
                current_config.gain = gain

            # Set new configuration
            return await self.set_electrode(position, current_config, timeout)
        except Exception as error:
            raise Exception(f"Couldn't enable electrode {position}. {error}")

    async def disable_electrode(
        self, position: str, timeout: int = 1000
    ) -> ElectrodeResponse:
        """Disable a specific electrode.

        Parameters
        ----------
        position : str
            Position of the electrode (e.g., "PZ", "O1", "O2")
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        ElectrodeResponse
            Response from the disable operation

        Raises
        ------
        ValueError
            If the position is not valid
        Exception
            If the request fails

        Examples
        --------
        >>> # Disable the PZ electrode
        >>> response = await device.electrode_manager.disable_electrode("PZ")
        >>> if response.success:
        ...     print("Electrode disabled successfully")
        """
        if position not in self._positions:
            raise ValueError(f"Invalid electrode position: {position}")

        try:
            # Get current configuration
            current_config = await self.get_electrode(position, timeout)

            # Update configuration
            current_config.enabled = False

            # Set new configuration
            return await self.set_electrode(position, current_config, timeout)
        except Exception as error:
            raise Exception(f"Couldn't disable electrode {position}. {error}")
