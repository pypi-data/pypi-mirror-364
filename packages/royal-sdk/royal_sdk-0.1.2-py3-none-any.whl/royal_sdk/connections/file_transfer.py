#https://docs.royalapps.com/r2023/scripting/objects/connections/royalfiletransferconnection.html
import platform
from enum import Enum
class FileTransferConnectionType(Enum):
    SFTP = "SFTP"

    def __str__(self):
        return self.value


class FileTransferConnection:
    def __init__(self, conn_type: FileTransferConnectionType, name: str, host: str, port: int=22):
        self.name = name
        self.host = host
        self.port = port
        self.conn_type= conn_type
        self.is_windows=None
        self.local_path=""
        self.remote_path=""

        self.credential = None

    def set_credential(self, cred):
        self.credential = cred

    def set_local_path(self,local_path: str,is_windows: bool=None):
        self.local_path = local_path
        self.is_windows = is_windows

    def set_remote_path(self,remote_path: str):
        self.remote_path = remote_path

    def objectify(self) -> dict:
        obj={
            "Type": "FileTransferConnection",
            "FileTransferConnectionType": str(self.conn_type),
            "Name": self.name,
            "ComputerName": self.host,
            "Port": self.port,
            "CredentialID": self.credential.cred_id if self.credential else None,
            "Properties": {},
        }

        # Local Path
        if self.local_path == "":
            obj["Properties"]["InitialLocalPathMode"] = 3 # 3 = Downloads
        else :
            obj["Properties"]["InitialLocalPathMode"] = 0 # 0 = Custom
            
            if self.is_windows is None:
                is_windows=platform.system() == 'Windows'
            else:
                is_windows=self.is_windows
            
            if is_windows:
                obj["Properties"]["InitialLocalPathWin"] = self.local_path
            else:
                obj["Properties"]["InitialLocalPathMac"] = self.local_path
                
        # Remote Path
        if self.remote_path == "":
            obj["Properties"]["InitialRemotePathMode"] = 0 # 0 = Automatic
        else:
            obj["Properties"]["InitialRemotePathMode"] = 1 # 1 = Custom
            obj["Properties"]["InitialRemotePath"] = self.remote_path
            
        return obj