"""
Communication-related exceptions for ELM327 adapter interaction.
"""


class CommunicationError(Exception):
    """Base exception for communication errors."""
    pass


class ConnectionError(CommunicationError):
    """Raised when connection to device fails."""
    pass


class TimeoutError(CommunicationError):
    """Raised when command times out."""
    pass


class DeviceNotFoundError(CommunicationError):
    """Raised when no ELM327 device is found."""
    pass


class ProtocolError(CommunicationError):
    """Raised when protocol-level error occurs."""
    pass


class InvalidResponseError(CommunicationError):
    """Raised when device returns invalid or unexpected response."""
    pass
