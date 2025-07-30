import json


class DynamicFolder:
    def __init__(self):
        self.Objects=[]

    def add(self,obj: dict):
        self.Objects.append(obj)

    def execute(self):
       print(json.dumps({
		"Objects": self.Objects
	}))
