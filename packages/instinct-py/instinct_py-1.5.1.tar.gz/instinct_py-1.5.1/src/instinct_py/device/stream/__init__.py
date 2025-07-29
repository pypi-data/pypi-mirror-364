"""
Stream module for data processing streams.

This module provides classes for creating and managing data
processing streams on the device.
"""

from instinct_py.device.stream.manager import InstinctDeviceStreamsManager
from instinct_py.device.stream.node import Node
from instinct_py.device.stream.pipe import Pipe
from instinct_py.device.stream.stream import Stream
from instinct_py.device.stream.types import (
    StreamConfig,
    StreamNodeConfig,
    StreamPipeConfig,
    StreamResponse,
    StreamSignal,
    NodeResponse,
    PipeResponse,
)

__all__ = [
    "InstinctDeviceStreamsManager",
    "Node",
    "Pipe",
    "Stream",
    "StreamConfig",
    "StreamNodeConfig",
    "StreamPipeConfig",
    "StreamResponse",
    "StreamSignal",
    "NodeResponse",
    "PipeResponse",
]
