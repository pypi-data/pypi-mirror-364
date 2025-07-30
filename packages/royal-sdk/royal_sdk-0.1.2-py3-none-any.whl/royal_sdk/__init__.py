
# Import main classes
from .credential import UsernameAndPassword, PrivateKey
from .folder import Folder
from .dynamic_folder import DynamicFolder
from .task import KeySequenceTask
from .connections.terminal import TerminalConnection, TerminalConnectionType
from .connections.file_transfer import FileTransferConnection, FileTransferConnectionType

__version__ = "0.1.2"
__all__ = [
    "UsernameAndPassword", 
    "PrivateKey",
    "Folder",
    "DynamicFolder",
    "KeySequenceTask",
    "TerminalConnection", 
    "TerminalConnectionType",
    "FileTransferConnection", 
    "FileTransferConnectionType"
]
