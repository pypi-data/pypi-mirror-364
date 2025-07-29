"""
Pipe module for connecting nodes in a stream.

This module provides the Pipe class for creating and managing
connections between nodes in a data processing stream.
"""

from typing import Any, Dict, Optional

from instinct_py.device.configuration.base import InstinctDeviceStreamsConfiguration
from instinct_py.device.stream.types import PipeResponse, StreamPipeConfig
from instinct_py.utils.http_client import HttpClient


class Pipe:
    """Represents a connection between nodes in a stream.

    Parameters
    ----------
    stream : Any
        The parent Stream instance
    config : StreamPipeConfig
        Configuration for the pipe
    """

    def __init__(self, stream: Any, config: StreamPipeConfig) -> None:
        """Initialize a pipe with the given configuration.

        Parameters
        ----------
        stream : Any
            The parent Stream instance
        config : StreamPipeConfig
            Configuration for the pipe
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
        """Get the pipe ID.

        Returns
        -------
        str
            The pipe ID
        """
        return self._config.id

    @property
    def source(self) -> str:
        """Get the source node ID.

        Returns
        -------
        str
            The source node ID
        """
        return self._config.source

    @property
    def destination(self) -> str:
        """Get the destination node ID.

        Returns
        -------
        str
            The destination node ID
        """
        return self._config.destination

    @property
    def config(self) -> StreamPipeConfig:
        """Get the pipe configuration.

        Returns
        -------
        StreamPipeConfig
            The pipe configuration
        """
        return self._config

    async def create(self, timeout: int = 1000) -> PipeResponse:
        """Create the pipe on the device.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        PipeResponse
            Response from the create operation

        Raises
        ------
        Exception
            If the request fails
        """
        try:
            response = self._http_client.post(
                self._streams_configuration.url_pipe_create,
                json={
                    "streamId": self._stream.id,
                    "pipe": self._config.model_dump(),
                },
                timeout=timeout / 1000,
            )
            return PipeResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't create pipe. {error}")

    async def delete(self, timeout: int = 1000) -> PipeResponse:
        """Delete the pipe from the stream.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        PipeResponse
            Response from the delete operation

        Raises
        ------
        Exception
            If the request fails
        """
        try:
            response = self._http_client.delete(
                f"{self._streams_configuration.url_pipe_delete}/{self._stream.id}/{self.id}",
                timeout=timeout / 1000,
            )
            return PipeResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't delete pipe. {error}")
