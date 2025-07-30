# Royal SDK

A Python SDK for Royal TSX/TS services, allowing you to programmatically create and manage connections, credentials, and folders.

## Installation

```bash
pip install royal-sdk
```

## Quick Start

### Basic Usage

```python
from royal_sdk import (
    DynamicFolder, 
    TerminalConnection, 
    TerminalConnectionType,
    FileTransferConnection,
    FileTransferConnectionType,
    UsernameAndPassword,
    Folder
)

# Create a dynamic folder (for Royal TSX dynamic folder scripts)
folder = DynamicFolder()

# Create credentials
cred = UsernameAndPassword(
    cred_id=1,
    name="My Server Credentials", 
    username="admin",
    password="secret123"
)

# Create SSH terminal connection
ssh_conn = TerminalConnection(
    conn_type=TerminalConnectionType.SSH,
    name="Production Server",
    host="192.168.1.100",
    port=22
)
ssh_conn.set_credential(cred)

# Create SFTP file transfer connection
sftp_conn = FileTransferConnection(
    conn_type=FileTransferConnectionType.SFTP,
    name="File Transfer",
    host="192.168.1.100",
    port=22
)
sftp_conn.set_credential(cred)
sftp_conn.set_local_path("/Users/username/Downloads")
sftp_conn.set_remote_path("/home/admin")

# Add connections to folder
folder.add(cred.objectify())
folder.add(ssh_conn.objectify())
folder.add(sftp_conn.objectify())

# Output the dynamic folder JSON
folder.execute()
```

### Creating Static Folders

```python
from royal_sdk import Folder, TerminalConnection, TerminalConnectionType

# Create connections
conn1 = TerminalConnection(
    conn_type=TerminalConnectionType.SSH,
    name="Server 1",
    host="server1.example.com"
)

conn2 = TerminalConnection(
    conn_type=TerminalConnectionType.SSH,
    name="Server 2", 
    host="server2.example.com"
)

# Create a static folder
server_folder = Folder("Production Servers", [
    conn1.objectify(),
    conn2.objectify()
])

print(server_folder.objectify())
```

## API Reference

### Credentials

#### UsernameAndPassword
Create username/password credentials.

```python
cred = UsernameAndPassword(
    cred_id=1,
    name="My Credentials",
    username="user",
    password="pass"
)
```

#### PrivateKey
Create private key credentials.

```python
from royal_sdk import PrivateKey

cred = PrivateKey(
    cred_id=2,
    name="SSH Key",
    private_key_content="-----BEGIN PRIVATE KEY-----...",
    passphrase="key_passphrase"
)
```

### Connections

#### TerminalConnection
Create SSH terminal connections.

```python
from royal_sdk import TerminalConnection, TerminalConnectionType

conn = TerminalConnection(
    conn_type=TerminalConnectionType.SSH,
    name="My Server",
    host="example.com",
    port=22  # optional, defaults to 22
)
```

#### FileTransferConnection  
Create SFTP file transfer connections.

```python
from royal_sdk import FileTransferConnection, FileTransferConnectionType

conn = FileTransferConnection(
    conn_type=FileTransferConnectionType.SFTP,
    name="File Server", 
    host="files.example.com",
    port=22  # optional, defaults to 22
)

# Set local and remote paths
conn.set_local_path("/Users/username/Downloads")
conn.set_remote_path("/home/user/files")
```

### Folders

#### DynamicFolder
For Royal TSX dynamic folder scripts.

```python
from royal_sdk import DynamicFolder

folder = DynamicFolder()
folder.add(connection.objectify())
folder.execute()  # Outputs JSON to stdout
```

#### Folder
For static folder structures.

```python
from royal_sdk import Folder

folder = Folder("My Folder", [
    connection1.objectify(),
    connection2.objectify()
])
```

## License

MIT
