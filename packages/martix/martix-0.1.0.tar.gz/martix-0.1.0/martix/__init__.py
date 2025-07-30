"""
Martix - A simplified Matrix client library for Python.

This library provides a high-level interface for working with Matrix protocol,
inspired by python-telegram-bot's design patterns.
"""

from .client import Client
from .types import Message, Command, User, Room, File, Audio, Photo, Document
from .events import EventHandler
from .exceptions import MartixError, AuthenticationError, NetworkError

__version__ = "1.0.0"
__author__ = "Martix Team"

__all__ = [
    "Client",
    "Message", 
    "Command",
    "User",
    "Room", 
    "File",
    "Audio",
    "Photo", 
    "Document",
    "EventHandler",
    "MartixError",
    "AuthenticationError", 
    "NetworkError"
]