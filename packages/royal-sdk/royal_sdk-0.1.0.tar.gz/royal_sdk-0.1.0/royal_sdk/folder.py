#https://docs.royalapps.com/r2023/scripting/objects/organization/royalfolder.html

class Folder:
    def __init__(self, name: str, objects: list[dict]):
        self.name = name
        self.objects = objects

    def add(self, obj: dict):
        self.objects.append(obj)

    def objectify(self) -> dict:
        return {
            "Type": "Folder",
            "Name": self.name,
            "Objects": self.objects,
        }
