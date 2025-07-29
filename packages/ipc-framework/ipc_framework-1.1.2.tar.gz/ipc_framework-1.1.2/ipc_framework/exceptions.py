"""
Custom exceptions for the IPC Framework
"""


class IPCError(Exception):
    """Base exception for IPC Framework"""
    pass


class ConnectionError(IPCError):
    """Raised when connection-related errors occur"""
    pass


class RoutingError(IPCError):
    """Raised when message routing fails"""
    pass


class AuthenticationError(IPCError):
    """Raised when authentication fails"""
    pass


class ChannelError(IPCError):
    """Raised when channel operations fail"""
    pass


class ApplicationError(IPCError):
    """Raised when application operations fail"""
    pass


class SerializationError(IPCError):
    """Raised when message serialization/deserialization fails"""
    pass


class TimeoutError(IPCError):
    """Raised when operations timeout"""
    pass 