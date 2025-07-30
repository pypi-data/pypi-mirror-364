"""Connections module for Royal SDK."""

from .terminal import TerminalConnection, TerminalConnectionType
from .file_transfer import FileTransferConnection, FileTransferConnectionType

__all__ = [
    "TerminalConnection", 
    "TerminalConnectionType",
    "FileTransferConnection", 
    "FileTransferConnectionType"
]
