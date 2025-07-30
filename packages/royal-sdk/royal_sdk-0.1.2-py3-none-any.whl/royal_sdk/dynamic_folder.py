import json


class DynamicFolder:
    def __init__(self,objects: list[dict]=[]):
        self.Objects=objects

    def add(self,obj: dict):
        self.Objects.append(obj)

    def execute(self):
       print(json.dumps({
		"Objects": self.Objects
	}))
