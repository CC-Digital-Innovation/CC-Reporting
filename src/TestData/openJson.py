import json

# Logic to be inherited in other files that reads json files and loads them as objects
class JsonFileReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.json_data = self.read_json()

    def read_json(self):
        try:
            with open(self.filepath, "r") as json_file:
                return json.load(json_file)
        except Exception as e:
            return None, e