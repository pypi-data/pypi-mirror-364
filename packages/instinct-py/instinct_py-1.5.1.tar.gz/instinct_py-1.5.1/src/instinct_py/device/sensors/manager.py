"""
Sensors manager module.

This module provides the InstinctDeviceSensorsManager class for managing
sensor configurations on the device.
"""

from typing import Any, Dict, List, Optional, Union

from instinct_py.device.sensors.types import SensorConfig, SensorResponse
from instinct_py.utils.http_client import HttpClient


class InstinctDeviceSensorsManager:
    """Manager for sensor configuration and data.

    Provides methods for configuring and reading data from sensors.

    Parameters
    ----------
    device : Any
        The parent InstinctDevice instance
    """

    def __init__(self, device: Any) -> None:
        """Initialize the sensors manager.

        Parameters
        ----------
        device : Any
            The parent InstinctDevice instance
        """
        self._device = device
        self._http_client = HttpClient()
        self._sensors_base_url = f"{device.base_configuration.system_base}/sensors"

    async def get_sensor(self, sensor_type: str, timeout: int = 1000) -> SensorConfig:
        """Get configuration for a specific sensor.

        Parameters
        ----------
        sensor_type : str
            Type of the sensor (e.g., "accelerometer", "gyroscope")
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        SensorConfig
            Configuration for the sensor

        Raises
        ------
        Exception
            If the request fails or the sensor type doesn't exist

        Examples
        --------
        >>> # Get configuration for the accelerometer
        >>> sensor = await device.sensor_manager.get_sensor("accelerometer")
        >>> print(f"Accelerometer enabled: {sensor.enabled}")
        """
        try:
            response = self._http_client.get(
                f"{self._sensors_base_url}/{sensor_type}",
                timeout=timeout / 1000,
            )
            return SensorConfig.model_validate(response)
        except Exception as error:
            raise Exception(
                f"Couldn't get sensor configuration for {sensor_type}. {error}"
            )

    async def set_sensor(
        self,
        sensor_type: str,
        config: Union[Dict[str, Any], SensorConfig],
        timeout: int = 1000,
    ) -> SensorResponse:
        """Configure a specific sensor.

        Parameters
        ----------
        sensor_type : str
            Type of the sensor (e.g., "accelerometer", "gyroscope")
        config : Union[Dict[str, Any], SensorConfig]
            Configuration for the sensor
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        SensorResponse
            Response from the configuration operation

        Raises
        ------
        Exception
            If the request fails or the sensor type doesn't exist

        Examples
        --------
        >>> # Enable the accelerometer with sample rate of 100 Hz
        >>> response = await device.sensor_manager.set_sensor(
        ...     "accelerometer",
        ...     {
        ...         "type": "accelerometer",
        ...         "enabled": True,
        ...         "sample_rate": 100,
        ...     }
        ... )
        >>> if response.success:
        ...     print("Sensor configured successfully")
        """
        # Convert to SensorConfig if it's a dict
        if isinstance(config, dict):
            sensor_config = SensorConfig(**config)
        else:
            sensor_config = config

        # Ensure type in config matches the requested type
        if sensor_config.type != sensor_type:
            raise ValueError(f"Type mismatch: {sensor_type} vs {sensor_config.type}")

        try:
            response = self._http_client.patch(
                f"{self._sensors_base_url}/{sensor_type}",
                json=sensor_config.model_dump(),
                timeout=timeout / 1000,
            )
            return SensorResponse.model_validate(response)
        except Exception as error:
            raise Exception(
                f"Couldn't set sensor configuration for {sensor_type}. {error}"
            )

    async def list_sensors(self, timeout: int = 1000) -> List[SensorConfig]:
        """List configurations for all sensors.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        List[SensorConfig]
            List of sensor configurations

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # List all sensor configurations
        >>> sensors = await device.sensor_manager.list_sensors()
        >>> for sensor in sensors:
        ...     print(f"{sensor.type}: {'enabled' if sensor.enabled else 'disabled'}")
        """
        try:
            response = self._http_client.get(
                self._sensors_base_url,
                timeout=timeout / 1000,
            )
            return [SensorConfig.model_validate(item) for item in response]
        except Exception as error:
            raise Exception(f"Couldn't list sensor configurations. {error}")

    async def enable_sensor(
        self,
        sensor_type: str,
        sample_rate: Optional[int] = None,
        range_value: Optional[float] = None,
        timeout: int = 1000,
    ) -> SensorResponse:
        """Enable a specific sensor.

        Parameters
        ----------
        sensor_type : str
            Type of the sensor (e.g., "accelerometer", "gyroscope")
        sample_rate : Optional[int], optional
            Sample rate in Hz, by default None
        range_value : Optional[float], optional
            Measurement range, by default None
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        SensorResponse
            Response from the enable operation

        Raises
        ------
        Exception
            If the request fails or the sensor type doesn't exist

        Examples
        --------
        >>> # Enable the accelerometer
        >>> response = await device.sensor_manager.enable_sensor("accelerometer")
        >>> if response.success:
        ...     print("Sensor enabled successfully")
        """
        try:
            # Get current configuration
            current_config = await self.get_sensor(sensor_type, timeout)

            # Update configuration
            current_config.enabled = True
            if sample_rate is not None:
                current_config.sample_rate = sample_rate
            if range_value is not None:
                current_config.range = range_value

            # Set new configuration
            return await self.set_sensor(sensor_type, current_config, timeout)
        except Exception as error:
            raise Exception(f"Couldn't enable sensor {sensor_type}. {error}")

    async def disable_sensor(
        self, sensor_type: str, timeout: int = 1000
    ) -> SensorResponse:
        """Disable a specific sensor.

        Parameters
        ----------
        sensor_type : str
            Type of the sensor (e.g., "accelerometer", "gyroscope")
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        SensorResponse
            Response from the disable operation

        Raises
        ------
        Exception
            If the request fails or the sensor type doesn't exist

        Examples
        --------
        >>> # Disable the accelerometer
        >>> response = await device.sensor_manager.disable_sensor("accelerometer")
        >>> if response.success:
        ...     print("Sensor disabled successfully")
        """
        try:
            # Get current configuration
            current_config = await self.get_sensor(sensor_type, timeout)

            # Update configuration
            current_config.enabled = False

            # Set new configuration
            return await self.set_sensor(sensor_type, current_config, timeout)
        except Exception as error:
            raise Exception(f"Couldn't disable sensor {sensor_type}. {error}")
