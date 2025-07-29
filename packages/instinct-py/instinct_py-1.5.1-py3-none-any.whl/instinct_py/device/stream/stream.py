"""
Stream module for data processing streams.

This module provides the Stream class for creating and managing
data processing streams on the device.
"""

from typing import Any, Dict, List, Optional, Union

from instinct_py.device.configuration.base import InstinctDeviceStreamsConfiguration
from instinct_py.device.stream.node import Node
from instinct_py.device.stream.pipe import Pipe
from instinct_py.device.stream.types import (
    StreamConfig,
    StreamNodeConfig,
    StreamPipeConfig,
    StreamResponse,
    StreamSignal,
)
from instinct_py.utils.http_client import HttpClient


class Stream:
    """Represents a data processing stream with nodes and pipes.

    Parameters
    ----------
    device : Any
        The parent InstinctDevice instance
    config : StreamConfig
        Configuration for the stream
    """

    def __init__(self, device: Any, config: StreamConfig) -> None:
        """Initialize a stream with the given configuration.

        Parameters
        ----------
        device : Any
            The parent device instance
        config : StreamConfig
            Configuration for the stream
        """
        self._device = device
        self._config = config
        self._http_client = HttpClient()
        self._streams_configuration = InstinctDeviceStreamsConfiguration(
            device.base_configuration
        )

        # Create Node and Pipe objects for each node and pipe in the config
        self._nodes = {node.id: Node(self, node) for node in config.nodes}
        self._pipes = {pipe.id: Pipe(self, pipe) for pipe in config.pipes}

    @property
    def id(self) -> str:
        """Get the stream ID.

        Returns
        -------
        str
            The stream ID
        """
        return self._config.id

    @property
    def config(self) -> StreamConfig:
        """Get the stream configuration.

        Returns
        -------
        StreamConfig
            The stream configuration
        """
        return self._config

    @property
    def nodes(self) -> Dict[str, Node]:
        """Get the nodes in the stream.

        Returns
        -------
        Dict[str, Node]
            Dictionary of nodes keyed by node ID
        """
        return self._nodes

    @property
    def pipes(self) -> Dict[str, Pipe]:
        """Get the pipes in the stream.

        Returns
        -------
        Dict[str, Pipe]
            Dictionary of pipes keyed by pipe ID
        """
        return self._pipes

    async def create(self, timeout: int = 5000) -> StreamResponse:
        """Create the stream on the device.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 5000

        Returns
        -------
        StreamResponse
            Response from the create operation

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # Create a stream on the device
        >>> await stream.create()
        """
        try:
            response = self._http_client.post(
                self._streams_configuration.url_stream_create,
                json=self._config.model_dump(),
                timeout=timeout / 1000,
            )
            return StreamResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't create stream. {error}")

    async def start(self, timeout: int = 1000) -> StreamResponse:
        """Start data processing on the stream.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        StreamResponse
            Response from the start operation

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # Start a stream for data processing
        >>> await stream.start()
        """
        try:
            response = self._http_client.post(
                self._streams_configuration.url_stream_start,
                json={"streamId": self.id},
                timeout=timeout / 1000,
            )
            return StreamResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't start stream. {error}")

    async def stop(self, timeout: int = 1000) -> StreamResponse:
        """Stop data processing on the stream.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        StreamResponse
            Response from the stop operation

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # Stop a running stream
        >>> await stream.stop()
        """
        try:
            response = self._http_client.post(
                self._streams_configuration.url_stream_stop,
                json={"streamId": self.id},
                timeout=timeout / 1000,
            )
            return StreamResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't stop stream. {error}")

    async def send_signal(
        self,
        signal: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: int = 1000,
    ) -> StreamResponse:
        """Send a signal to the stream.

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
        StreamResponse
            Response from the signal operation

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # Send a custom signal to the stream
        >>> await stream.send_signal("custom_command", {"param1": "value1"})
        """
        try:
            response = self._http_client.post(
                self._streams_configuration.url_stream_signal,
                json={
                    "streamId": self.id,
                    "signal": StreamSignal(
                        signal=signal,
                        parameters=parameters or {},
                    ).model_dump(),
                },
                timeout=timeout / 1000,
            )
            return StreamResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't send signal to stream. {error}")

    async def reconcile(self, timeout: int = 1000) -> StreamResponse:
        """Reconcile the stream configuration to adapt to changes.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        StreamResponse
            Response from the reconcile operation

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # After adding or removing nodes/pipes, reconcile the stream
        >>> await stream.reconcile()
        """
        try:
            response = self._http_client.post(
                self._streams_configuration.url_stream_reconcile,
                json={"streamId": self.id},
                timeout=timeout / 1000,
            )
            return StreamResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't reconcile stream. {error}")

    async def delete(self, timeout: int = 1000) -> StreamResponse:
        """Delete the stream from the device.

        Parameters
        ----------
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        StreamResponse
            Response from the delete operation

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # Delete a stream when no longer needed
        >>> await stream.delete()
        """
        try:
            response = self._http_client.delete(
                f"{self._streams_configuration.url_stream_delete}/{self.id}",
                timeout=timeout / 1000,
            )
            return StreamResponse.model_validate(response)
        except Exception as error:
            raise Exception(f"Couldn't delete stream. {error}")

    async def add_nodes(
        self, nodes: List[Union[Dict[str, Any], StreamNodeConfig]], timeout: int = 1000
    ) -> Dict[str, Node]:
        """Add new nodes to the stream.

        Parameters
        ----------
        nodes : List[Union[Dict[str, Any], StreamNodeConfig]]
            List of node configurations to add
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        Dict[str, Node]
            Dictionary of added nodes keyed by node ID

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # Add a new node to the stream
        >>> new_nodes = await stream.add_nodes([{
        ...     "executable": "another_custom_node",
        ...     "config": {
        ...         "threshold": 0.75,
        ...         "windowSize": 256,
        ...     },
        ...     "meta": {
        ...         "author": "Nexstem",
        ...         "version": "1.1.0",
        ...     },
        ... }])
        """
        added_nodes = {}

        # Convert dict configs to StreamNodeConfig objects
        node_configs = [
            n if isinstance(n, StreamNodeConfig) else StreamNodeConfig(**n)
            for n in nodes
        ]

        # Create Node objects
        for node_config in node_configs:
            node = Node(self, node_config)
            await node.create(timeout)

            # Update internal nodes dictionary
            self._nodes[node.id] = node
            added_nodes[node.id] = node

            # Update stream config
            self._config.nodes.append(node_config)

        return added_nodes

    async def delete_node(self, node_id: str, timeout: int = 1000) -> bool:
        """Delete a node from the stream.

        Parameters
        ----------
        node_id : str
            ID of the node to delete
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        bool
            True if the node was deleted successfully

        Raises
        ------
        Exception
            If the request fails or the node doesn't exist

        Examples
        --------
        >>> # Delete a node from the stream
        >>> success = await stream.delete_node(node_id)
        >>> if success:
        ...     print("Node deleted successfully")
        """
        if node_id not in self._nodes:
            raise ValueError(f"Node with ID '{node_id}' not found in stream")

        # Delete the node
        node = self._nodes[node_id]
        await node.delete(timeout)

        # Remove from internal dictionaries
        del self._nodes[node_id]

        # Update stream config
        self._config.nodes = [n for n in self._config.nodes if n.id != node_id]

        return True

    async def add_pipes(
        self, pipes: List[Union[Dict[str, Any], StreamPipeConfig]], timeout: int = 1000
    ) -> Dict[str, Pipe]:
        """Add new pipes to the stream.

        Parameters
        ----------
        pipes : List[Union[Dict[str, Any], StreamPipeConfig]]
            List of pipe configurations to add
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        Dict[str, Pipe]
            Dictionary of added pipes keyed by pipe ID

        Raises
        ------
        Exception
            If the request fails

        Examples
        --------
        >>> # Add a new pipe to the stream
        >>> new_pipes = await stream.add_pipes([{
        ...     "source": "source_node_id",
        ...     "destination": "destination_node_id",
        ... }])
        """
        added_pipes = {}

        # Convert dict configs to StreamPipeConfig objects
        pipe_configs = [
            p if isinstance(p, StreamPipeConfig) else StreamPipeConfig(**p)
            for p in pipes
        ]

        # Create Pipe objects
        for pipe_config in pipe_configs:
            pipe = Pipe(self, pipe_config)
            await pipe.create(timeout)

            # Update internal pipes dictionary
            self._pipes[pipe.id] = pipe
            added_pipes[pipe.id] = pipe

            # Update stream config
            self._config.pipes.append(pipe_config)

        return added_pipes

    async def delete_pipe(self, pipe_id: str, timeout: int = 1000) -> bool:
        """Delete a pipe from the stream.

        Parameters
        ----------
        pipe_id : str
            ID of the pipe to delete
        timeout : int, optional
            Timeout in milliseconds for the request, by default 1000

        Returns
        -------
        bool
            True if the pipe was deleted successfully

        Raises
        ------
        Exception
            If the request fails or the pipe doesn't exist

        Examples
        --------
        >>> # Delete a pipe from the stream
        >>> success = await stream.delete_pipe(pipe_id)
        >>> if success:
        ...     print("Pipe deleted successfully")
        """
        if pipe_id not in self._pipes:
            raise ValueError(f"Pipe with ID '{pipe_id}' not found in stream")

        # Delete the pipe
        pipe = self._pipes[pipe_id]
        await pipe.delete(timeout)

        # Remove from internal dictionaries
        del self._pipes[pipe_id]

        # Update stream config
        self._config.pipes = [p for p in self._config.pipes if p.id != pipe_id]

        return True
