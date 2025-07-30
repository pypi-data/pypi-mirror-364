# https://docs.royalapps.com/r2023/scripting/objects/organization/royalcredential.html
class UsernameAndPassword:
    def __init__(self,cred_id: int,name: str,username: str,password: str):
        self.cred_id=cred_id
        self.name=name
        self.username=username
        self.password=password

    def objectify(self) -> dict:
        return {
                "Type": "Credential",
                "ID": str(self.cred_id),
                "Name": self.name,
                "Username": self.username,
                "Password": self.password,
                "Path": "/Credentials",
            }

class PrivateKey:
    def __init__(self,cred_id: int,name: str,private_key_content: str,passphrase: str):
        self.cred_id=cred_id
        self.name=name
        self.private_key_content=private_key_content
        self.passphrase=passphrase

    def objectify(self) -> dict:
        return {
                "Type": "Credential",
                "PrivateKeyMode":1, # 1 = Embedded
                "ID": str(self.cred_id),
                "Name": self.name,
                "PrivateKeyContent": self.private_key_content,
                "Passphrase": self.passphrase,
                "Path": "/Credentials"
            }

class PrivateKeyWithPath:
	def __init__(self,cred_id: int,name: str,path: str,passphrase: str):
		self.cred_id=cred_id
		self.name=name
		self.path=path
		self.passphrase=passphrase
		

	def objectify(self) -> dict:
		return {
				"Type": "Credential",
                "PrivateKeyMode":0, # 0 = Path to file
				"ID": str(self.cred_id),
				"Name": self.name,
                "PrivateKeyPath": self.path,
                "Passphrase": self.passphrase,
				"Path": "/Credentials"
			}
	
