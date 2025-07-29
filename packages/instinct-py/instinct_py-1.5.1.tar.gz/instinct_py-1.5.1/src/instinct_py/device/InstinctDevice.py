"""
Core module for interacting with Nexstem Instinct devices.

This module contains the main InstinctDevice class that serves as the primary entry point
for discovering, connecting to, and controlling Instinct devices.
"""

import socket
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import BaseModel

from instinct_py.device.configuration.base import (
    InstinctDeviceBaseConfiguration,
    InstinctDeviceSystemConfiguration,
)
from instinct_py.device.device_config.manager import InstinctDeviceConfigManager
from instinct_py.device.electrode.manager import InstinctDeviceElectrodesManager
from instinct_py.device.sensors.manager import InstinctDeviceSensorsManager
from instinct_py.device.stream.manager import InstinctDeviceStreamsManager
from instinct_py.utils.http_client import HttpClient


class DebugCommand(BaseModel):
    """Debug command interface for low-level hardware interaction.

    Used for sending direct commands to device peripherals.
    """

    cmd_resp: int
    peripheral: int
    peripheral_channels: int
    parameter: List[int]
    data: List[int]
    packet_type: int


class InstinctDeviceBattery(BaseModel):
    """Battery status and information for the device."""

    hasBattery: bool
    cycleCount: int
    isCharging: int
    designedCapacity: int
    maxCapacity: int
    currentCapacity: int
    voltage: int
    percent: int
    capacityUnit: str
    timeRemaining: int | None
    acConnected: bool
    type: str
    model: str
    manufacturer: str
    serial: str


class InstinctDeviceCPU(BaseModel):
    """CPU status and information for the device."""

    load: float
    temperature: int
    totalClockSpeed: float
    currentClockSpeed: float


class InstinctDeviceRAM(BaseModel):
    """RAM status and information for the device."""

    total: int
    available: int
    free: int


class InstinctDeviceStorage(BaseModel):
    """Storage status and information for the device."""

    total: int
    free: int


class InstinctDeviceState(BaseModel):
    """Comprehensive state information for the device.

    Includes status, network configuration, and hardware metrics.
    """

    status: str
    httpPort: int
    grpcPort: int
    host: str
    battery: InstinctDeviceBattery
    cpu: InstinctDeviceCPU
    ram: InstinctDeviceRAM
    storage: InstinctDeviceStorage


class InstinctDeviceName(BaseModel):
    """Device name information."""

    name: str


class InstinctDeviceSetNameResponse(BaseModel):
    """Response for device name setting operation."""

    message: str
    success: bool


@dataclass
class InstinctDeviceConfig:
    """Configuration options for device initialization."""

    base_url: Optional[str] = None
    discovery_port: Optional[int] = None
    debug: bool = False
    services: Optional[Dict[str, str]] = None


class InstinctDevice:
    """The main Device class representing an Instinct device.

    Provides access to all device's functionality including streams, electrodes,
    and sensors. Serves as the primary entry point for the SDK.

    Parameters
    ----------
    host_address : str
        The IP address of the device
    config : Optional[DeviceConfig]
        Optional configuration parameters

    Attributes
    ----------
    host_address : str
        IP address of the device
    base_configuration : InstinctDeviceBaseConfiguration
        Base configuration for all services
    streams_manager : InstinctDeviceStreamsManager
        Manager for creating and controlling streams
    electrode_manager : InstinctDeviceElectrodesManager
        Manager for electrode configuration and data
    sensor_manager : InstinctDeviceSensorsManager
        Manager for sensor configuration and data
    device_config_manager : DeviceConfigManager
        Manager for device configuration storage
    """

    def __init__(
        self, host_address: str, config: Optional[InstinctDeviceConfig] = None
    ) -> None:
        """Initialize a Instinct Device instance for direct connection to a known device."""
        self.host_address = host_address

        # Set default config if none provided
        if config is None:
            config = InstinctDeviceConfig()

        self._is_debug_enabled = config.debug

        # Initialize configuration objects with provided or default settings
        system_base = None
        streams_base = None
        if config.services:
            system_base = config.services.get("system")
            streams_base = config.services.get("streams")

        self.base_configuration = InstinctDeviceBaseConfiguration(
            base_url=config.base_url, system_base=system_base, streams_base=streams_base
        )
        self._system_configuration = InstinctDeviceSystemConfiguration(
            self.base_configuration
        )

        # Standard 10-20 EEG electrode positions
        standard_electrodes = [
            "PZ",
            "O1",
            "O2",
            "P3",
            "P4",
            "T5",
            "T6",
            "C3",
            "C4",
            "T3",
            "T4",
            "CMS",
            "DRL",
            "CZ",
            "F7",
            "F8",
            "F3",
            "F4",
            "FP1",
            "FP2",
            "FZ",
        ]

        # Initialize managers
        self.electrode_manager = InstinctDeviceElectrodesManager(
            self, standard_electrodes
        )
        self.sensor_manager = InstinctDeviceSensorsManager(self)
        self.device_config_manager = InstinctDeviceConfigManager(self)
        self.streams_manager = InstinctDeviceStreamsManager(self)

        # Create HTTP client
        self._http_client = HttpClient()

    @property
    def streams_manager(self) -> InstinctDeviceStreamsManager:
        """Manager for creating and controlling streams."""
        return self._streams_manager

    @streams_manager.setter
    def streams_manager(self, value: InstinctDeviceStreamsManager) -> None:
        self._streams_manager = value

    @property
    def electrode_manager(self) -> InstinctDeviceElectrodesManager:
        """Manager for electrode configuration and data."""
        return self._electrode_manager

    @electrode_manager.setter
    def electrode_manager(self, value: InstinctDeviceElectrodesManager) -> None:
        self._electrode_manager = value

    @property
    def sensor_manager(self) -> InstinctDeviceSensorsManager:
        """Manager for sensor configuration and data."""
        return self._sensor_manager

    @sensor_manager.setter
    def sensor_manager(self, value: InstinctDeviceSensorsManager) -> None:
        self._sensor_manager = value

    @property
    def device_config_manager(self) -> InstinctDeviceConfigManager:
        """Manager for device configuration storage."""
        return self._device_config_manager

    @device_config_manager.setter
    def device_config_manager(self, value: InstinctDeviceConfigManager) -> None:
        self._device_config_manager = value

    @staticmethod
    def discover(
        timeout: int = 5, discovery_port: int = 48010, debug: bool = False
    ) -> List["InstinctDevice"]:
        """Discover all Instinct devices on the local network.

        Uses UDP broadcast to find devices and returns instances for each one found.

        Parameters
        ----------
        timeout : int, optional
            Timeout in seconds for the discovery process, by default 5
        discovery_port : int, optional
            Port to use for broadcasting discovery messages, by default 48010
        debug : bool, optional
            Whether to enable debug mode for discovered devices, by default False

        Returns
        -------
        List[InstinctDevice]
            List of InstinctDevice instances for discovered devices

        Raises
        ------
        Exception
            If there's a network error during the discovery process
        """
        discovered_devices: List[str] = []

        # Create broadcast and receive sockets
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Enable broadcasting
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Bind receive socket
            receive_socket.bind(("0.0.0.0", 0))
            receive_port = receive_socket.getsockname()[1]

            # Set non-blocking receive
            receive_socket.setblocking(False)

            # Format and send the discovery message
            message = f"INSTINCT_DISCOVER:{receive_port}".encode()
            broadcast_socket.sendto(message, ("255.255.255.255", discovery_port))

            # Wait for responses
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    data, addr = receive_socket.recvfrom(1024)
                    if addr[0] not in discovered_devices:
                        discovered_devices.append(addr[0])
                except BlockingIOError:
                    # No data available, continue polling
                    time.sleep(0.1)

            # Create InstinctDevice instances for each discovered device
            return [
                InstinctDevice(
                    device_ip,
                    InstinctDeviceConfig(
                        base_url=f"http://{device_ip}:42069",
                        debug=debug,
                        discovery_port=discovery_port,
                    ),
                )
                for device_ip in discovered_devices
            ]

        finally:
            # Clean up sockets
            broadcast_socket.close()
            receive_socket.close()

    def send_debug_command(
        self, command: DebugCommand, timeout: int = 1000
    ) -> DebugCommand:
        """Send a debug command to the device.

        Only available when debug mode is enabled.

        Parameters
        ----------
        command : DebugCommand
            The debug command to send
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        DebugCommand
            Command response from the device

        Raises
        ------
        ValueError
            If debug mode is not enabled
        Exception
            If the command fails
        """
        if not self._is_debug_enabled:
            raise ValueError("Debug mode is not enabled. Command failed.")

        try:
            response = self._http_client.post(
                self._system_configuration.url_device_send_debug_command,
                data=command.model_dump(),
                timeout=timeout / 1000,
            )
            return DebugCommand.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't send debug command. {error}")

    def get_state(self, timeout: int = 1000) -> InstinctDeviceState:
        """Get the current state of the device.

        Includes information about status, battery, CPU, RAM, and storage.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        InstinctDeviceState
            Comprehensive state information for the device

        Raises
        ------
        Exception
            If the request fails
        """
        try:
            response = self._http_client.get(
                self._system_configuration.url_device_get_state,
                timeout=timeout / 1000,
            )
            return InstinctDeviceState.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't get health of the device. {error}")

    def get_name(self, timeout: int = 1000) -> str:
        """Get the current name of the device.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        str
            The name of the device

        Raises
        ------
        Exception
            If the request fails
        """
        try:
            response = self._http_client.get(
                self._system_configuration.url_device_get_name,
                timeout=timeout / 1000,
            )
            device_name = InstinctDeviceName.model_validate(response)
            return device_name.name
        except Exception as error:
            raise Exception(f"Couldn't get name of the device. {error}")

    def set_name(self, name: str, timeout: int = 0) -> InstinctDeviceSetNameResponse:
        """Set a new name for the device.

        Parameters
        ----------
        name : str
            The new name for the device
        timeout : int, optional
            Timeout in milliseconds for the request (0 means no timeout), by default 0

        Returns
        -------
        InstinctDeviceSetNameResponse
            Response from the name-setting operation

        Raises
        ------
        Exception
            If the request fails
        """
        try:
            response = self._http_client.patch(
                self._system_configuration.url_device_set_name,
                data={"hostname": name},
                timeout=timeout / 1000 if timeout > 0 else None,
            )
            return InstinctDeviceSetNameResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't set name of the device. {error}")
