"""
Exception classes for Martix library.
"""


class MartixError(Exception):
    """
    Base exception class for Martix library.
    
    All Martix-specific exceptions inherit from this class.
    """
    pass


class AuthenticationError(MartixError):
    """
    Raised when authentication with Matrix homeserver fails.
    
    This exception is raised when login credentials are invalid
    or when authentication-related operations fail.
    """
    pass


class NetworkError(MartixError):
    """
    Raised when network-related operations fail.
    
    This exception is raised for connection timeouts, DNS resolution
    failures, and other network-related issues.
    """
    pass


class RoomError(MartixError):
    """
    Raised when room-related operations fail.
    
    This exception is raised when attempting to join non-existent rooms,
    perform operations without proper permissions, etc.
    """
    pass


class FileError(MartixError):
    """
    Raised when file operations fail.
    
    This exception is raised for file upload/download failures,
    invalid file formats, or file access issues.
    """
    pass


class CommandError(MartixError):
    """
    Raised when command processing fails.
    
    This exception is raised for command parsing errors or
    when command handlers encounter issues.
    """
    pass