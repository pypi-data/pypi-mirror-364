#https://docs.royalapps.com/r2023/scripting/objects/connections/royalsshconnection.html
from enum import Enum
class TerminalConnectionType(Enum):
    SSH = "SSH"
    
    def __str__(self):
        return self.value


class TerminalConnection:
    def __init__(self, conn_type: TerminalConnectionType, name: str, host: str, port: int=22):
        self.name = name
        self.host = host
        self.port = port
        self.conn_type= conn_type

        self.credential = None

    def set_credential(self, cred):
        self.credential = cred

    def objectify(self) -> dict:
        return {
            "Type": "TerminalConnection",
            "TerminalConnectionType": str(self.conn_type),
            "Name": self.name,
            "ComputerName": self.host,
            "Port": self.port,
            "CredentialID": self.credential.cred_id if self.credential else None
        }

    


