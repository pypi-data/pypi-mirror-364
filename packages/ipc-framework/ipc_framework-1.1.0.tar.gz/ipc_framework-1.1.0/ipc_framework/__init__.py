"""
IPC Framework - Efficient Inter-Process Communication Framework

A framework for handling client-server communication with hierarchical
application and channel management.
"""

from .core import IPCServer, IPCClient, Application, Channel, Message, MessageType
from .server import FrameworkServer
from .client import FrameworkClient
from .exceptions import IPCError, ConnectionError, RoutingError

__version__ = "1.0.0"
__author__ = "IPC Framework"

__all__ = [
    "IPCServer",
    "IPCClient", 
    "Application",
    "Channel",
    "Message",
    "MessageType",
    "FrameworkServer",
    "FrameworkClient",
    "IPCError",
    "ConnectionError",
    "RoutingError"
] 