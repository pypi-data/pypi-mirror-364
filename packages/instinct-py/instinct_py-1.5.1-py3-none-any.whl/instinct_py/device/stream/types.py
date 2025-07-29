"""
Type definitions for the stream processing subsystem.

This module defines the data models used for creating and managing
data processing streams on the device.
"""

from typing import Any, Dict, List, Optional

import uuid
from pydantic import BaseModel


class StreamNodeConfig(BaseModel):
    """Configuration for a stream processing node.

    Parameters
    ----------
    executable : str
        The executable name for the node
    config : Dict[str, Any]
        Configuration parameters for the node
    id : str
        Unique identifier for the node
    meta : Optional[Dict[str, Any]], optional
        Metadata for the node, by default None
    """

    executable: str
    config: Dict[str, Any]
    id: str
    meta: Optional[Dict[str, Any]] = None

    def __init__(self, **data: Any) -> None:
        """Initialize a stream node configuration.

        Generates a UUID if id is not provided.
        """
        if "id" not in data or data["id"] is None:
            data["id"] = str(uuid.uuid4())
        super().__init__(**data)


class StreamPipeConfig(BaseModel):
    """Configuration for a stream processing pipe.

    Parameters
    ----------
    source : str
        ID of the source node
    destination : str
        ID of the destination node
    id : str
        Unique identifier for the pipe
    """

    source: str
    destination: str
    id: str

    def __init__(self, **data: Any) -> None:
        """Initialize a stream pipe configuration.

        Generates a UUID if id is not provided.
        """
        if "id" not in data or data["id"] is None:
            data["id"] = str(uuid.uuid4())
        super().__init__(**data)


class StreamConfig(BaseModel):
    """Configuration for a data processing stream.

    Parameters
    ----------
    id : str
        Unique identifier for the stream
    nodes : List[StreamNodeConfig]
        List of processing nodes in the stream
    pipes : List[StreamPipeConfig]
        List of pipes connecting the nodes
    meta : Optional[Dict[str, Any]], optional
        Metadata for the stream, by default None
    """

    id: str
    nodes: List[StreamNodeConfig]
    pipes: List[StreamPipeConfig]
    meta: Optional[Dict[str, Any]] = None

    def __init__(self, **data: Any) -> None:
        """Initialize a stream configuration.

        Generates a UUID if id is not provided.
        Converts node and pipe dictionaries to their respective models.
        """
        if "id" not in data or data["id"] is None:
            data["id"] = str(uuid.uuid4())

        # Convert nodes and pipes from dicts to models if needed
        if "nodes" in data and isinstance(data["nodes"], list):
            data["nodes"] = [
                n if isinstance(n, StreamNodeConfig) else StreamNodeConfig(**n)
                for n in data["nodes"]
            ]

        if "pipes" in data and isinstance(data["pipes"], list):
            data["pipes"] = [
                p if isinstance(p, StreamPipeConfig) else StreamPipeConfig(**p)
                for p in data["pipes"]
            ]

        super().__init__(**data)


class StreamSignal(BaseModel):
    """Signal to be sent to a stream or node.

    Parameters
    ----------
    signal : str
        Type of signal to send
    parameters : Optional[Dict[str, Any]], optional
        Parameters for the signal, by default None
    """

    signal: str
    parameters: Optional[Dict[str, Any]] = None


class StreamResponse(BaseModel):
    """Response from stream operations.

    Parameters
    ----------
    message : str
        Response message
    success : bool
        Whether the operation was successful
    stream : Optional[StreamConfig], optional
        Stream configuration if applicable, by default None
    """

    message: str
    success: bool
    stream: Optional[StreamConfig] = None


class NodeResponse(BaseModel):
    """Response from node operations.

    Parameters
    ----------
    message : str
        Response message
    success : bool
        Whether the operation was successful
    node : Optional[StreamNodeConfig], optional
        Node configuration if applicable, by default None
    """

    message: str
    success: bool
    node: Optional[StreamNodeConfig] = None


class PipeResponse(BaseModel):
    """Response from pipe operations.

    Parameters
    ----------
    message : str
        Response message
    success : bool
        Whether the operation was successful
    pipe : Optional[StreamPipeConfig], optional
        Pipe configuration if applicable, by default None
    """

    message: str
    success: bool
    pipe: Optional[StreamPipeConfig] = None
