"""
Stream manager module.

This module provides the InstinctDeviceStreamsManager class for creating and
managing streams on the device.
"""

from typing import Any, Dict, List, Union

from instinct_py.device.configuration.base import InstinctDeviceStreamsConfiguration
from instinct_py.device.stream.stream import Stream
from instinct_py.device.stream.types import StreamConfig, StreamResponse
from instinct_py.utils.http_client import HttpClient


class InstinctDeviceStreamsManager:
    """Manager for creating and controlling data streams.

    Provides methods for creating, listing, and retrieving streams on the device.

    Parameters
    ----------
    device : Any
        The parent InstinctDevice instance
    """

    def __init__(self, device: Any) -> None:
        """Initialize the streams manager.

        Parameters
        ----------
        device : Any
            The parent device instance
        """
        self._device = device
        self._http_client = HttpClient()
        self._streams_configuration = InstinctDeviceStreamsConfiguration(
            device.base_configuration
        )
        self._streams: Dict[str, Stream] = {}

    def create_stream(self, config: Union[Dict[str, Any], StreamConfig]) -> Stream:
        """Create a new stream object (not yet created on the device).

        Parameters
        ----------
        config : Union[Dict[str, Any], StreamConfig]
            Configuration for the stream

        Returns
        -------
        Stream
            The created stream object

        Examples
        --------
        >>> # Create a stream with custom metadata
        >>> stream = device.streams_manager.create_stream({
        ...     "meta": {
        ...         "name": "Alpha Rhythm Analysis",
        ...         "description": "Extracts and analyzes alpha rhythms from occipital electrodes",
        ...         "version": "1.0.0",
        ...     },
        ...     "nodes": [
        ...         {
        ...             "executable": "eeg_source",
        ...             "config": {
        ...                 "sampleRate": 250,
        ...                 "channels": ["O1", "O2", "PZ"],
        ...             },
        ...         },
        ...         {
        ...             "executable": "bandpass_filter",
        ...             "config": {
        ...                 "cutoff": 10,
        ...                 "bandwidth": 4,
        ...                 "order": 4,
        ...             },
        ...         },
        ...     ],
        ...     "pipes": [
        ...         {
        ...             "source": "source_id",
        ...             "destination": "destination_id",
        ...         },
        ...     ],
        ... })
        >>>
        >>> # Create and start the stream
        >>> await stream.create()
        >>> await stream.start()
        """
        # Convert to StreamConfig if it's a dict
        if isinstance(config, dict):
            stream_config = StreamConfig(**config)
        else:
            stream_config = config

        # Create Stream object
        stream = Stream(self._device, stream_config)

        # Add to internal streams dictionary
        self._streams[stream.id] = stream

        return stream

    async def get_stream(self, stream_id: str, timeout: int = 1000) -> Stream:
        """Get a stream from the device by ID.

        Parameters
        ----------
        stream_id : str
            The ID of the stream to get
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        Stream
            The stream object

        Raises
        ------
        Exception
            If the request fails or the stream doesn't exist

        Examples
        --------
        >>> # Get a stream by ID
        >>> stream = await device.streams_manager.get_stream("stream_id")
        """
        # Check if the stream is already in the internal cache
        if stream_id in self._streams:
            return self._streams[stream_id]

        try:
            # Fetch the stream from the device
            response = self._http_client.get(
                f"{self._streams_configuration.url_stream_get}/{stream_id}",
                timeout=timeout / 1000,
            )

            # Create a Stream object
            stream_config = StreamConfig.model_validate(response)
            stream = Stream(self._device, stream_config)

            # Add to internal streams dictionary
            self._streams[stream.id] = stream

            return stream
        except Exception as error:
            raise Exception(f"Couldn't get stream with ID '{stream_id}'. {error}")

    async def list_streams(self, timeout: int = 1000) -> List[Stream]:
        """List all streams on the device.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        List[Stream]
            List of stream objects

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # List all streams on the device
        >>> streams = await device.streams_manager.list_streams()
        >>> for stream in streams:
        ...     print(f"Stream {stream.id}: {stream.config.meta.get('name', 'unnamed')}")
        """
        try:
            response = self._http_client.get(
                self._streams_configuration.url_stream_get,
                timeout=timeout / 1000,
            )

            streams = []
            for stream_data in response:
                stream_config = StreamConfig.model_validate(stream_data)
                stream = Stream(self._device, stream_config)

                # Update internal streams dictionary
                self._streams[stream.id] = stream
                streams.append(stream)

            return streams
        except Exception as error:
            raise Exception(f"Couldn't list streams. {error}")

    async def delete_stream(
        self, stream_id: str, timeout: int = 1000
    ) -> StreamResponse:
        """Delete a stream from the device.

        Parameters
        ----------
        stream_id : str
            The ID of the stream to delete
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        StreamResponse
            Response from the delete operation

        Raises
        ------
        Exception
            If the request fails or the stream doesn't exist

        Examples
        --------
        >>> # Delete a stream by ID
        >>> response = await device.streams_manager.delete_stream("stream_id")
        >>> if response.success:
        ...     print("Stream deleted successfully")
        """
        try:
            response = self._http_client.delete(
                f"{self._streams_configuration.url_stream_delete}/{stream_id}",
                timeout=timeout / 1000,
            )

            # Remove from internal streams dictionary
            if stream_id in self._streams:
                del self._streams[stream_id]

            return StreamResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't delete stream with ID '{stream_id}'. {error}")
