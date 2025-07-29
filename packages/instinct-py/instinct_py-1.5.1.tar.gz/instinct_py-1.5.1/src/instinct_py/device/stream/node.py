"""
Node module for processing nodes in a stream.

This module provides the Node class for creating and managing
processing nodes in a data processing stream.
"""

from typing import Any, Dict, Optional

from instinct_py.device.configuration.base import InstinctDeviceStreamsConfiguration
from instinct_py.device.stream.types import (
    NodeResponse,
    StreamNodeConfig,
    StreamSignal,
)
from instinct_py.utils.http_client import HttpClient


class Node:
    """Represents a processing node in a stream.

    Parameters
    ----------
    stream : Any
        The parent Stream instance
    config : StreamNodeConfig
        Configuration for the node
    """

    def __init__(self, stream: Any, config: StreamNodeConfig) -> None:
        """Initialize a node with the given configuration.

        Parameters
        ----------
        stream : Any
            The parent Stream instance
        config : StreamNodeConfig
            Configuration for the node
        """
        self._stream = stream
        self._config = config
        self._device = stream._device
        self._http_client = HttpClient()
        self._streams_configuration = InstinctDeviceStreamsConfiguration(
            self._device.base_configuration
        )

    @property
    def id(self) -> str:
        """Get the node ID.

        Returns
        -------
        str
            The node ID
        """
        return self._config.id

    @property
    def executable(self) -> str:
        """Get the node executable name.

        Returns
        -------
        str
            The executable name
        """
        return self._config.executable

    @property
    def config(self) -> StreamNodeConfig:
        """Get the node configuration.

        Returns
        -------
        StreamNodeConfig
            The node configuration
        """
        return self._config

    async def create(self, timeout: int = 1000) -> NodeResponse:
        """Create the node on the device.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        NodeResponse
            Response from the create operation

        Raises
        ------
        Exception
            If the request fails
        """
        try:
            response = self._http_client.post(
                self._streams_configuration.url_node_create,
                json={
                    "streamId": self._stream.id,
                    "node": self._config.model_dump(),
                },
                timeout=timeout / 1000,
            )
            return NodeResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't create node. {error}")

    async def send_signal(
        self,
        signal: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: int = 1000,
    ) -> NodeResponse:
        """Send a signal to the node.

        Parameters
        ----------
        signal : str
            The signal to send
        parameters : Optional[Dict[str, Any]], optional
            Parameters for the signal, by default None
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        NodeResponse
            Response from the signal operation

        Raises
        ------
        Exception
            If the request fails
        """
        try:
            response = self._http_client.post(
                self._streams_configuration.url_node_signal,
                json={
                    "streamId": self._stream.id,
                    "nodeId": self.id,
                    "signal": StreamSignal(
                        signal=signal,
                        parameters=parameters or {},
                    ).model_dump(),
                },
                timeout=timeout / 1000,
            )
            return NodeResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't send signal to node. {error}")

    async def delete(self, timeout: int = 1000) -> NodeResponse:
        """Delete the node from the stream.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        NodeResponse
            Response from the delete operation

        Raises
        ------
        Exception
            If the request fails
        """
        try:
            response = self._http_client.delete(
                f"{self._streams_configuration.url_node_delete}/{self._stream.id}/{self.id}",
                timeout=timeout / 1000,
            )
            return NodeResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't delete node. {error}")
