import json

# Logic to be inherited in other files that reads json files and either loads or dumps them using the json module
# Constructing JSON objects can be done in one line of code using this class


class jsonR():
    # Constructor
    # Takes in filepath and to_list as arguments
    def __init__(self, filepath):
        self.filepath = filepath


    # Method to be inherited and used in other files that loada json files as an object for simpler manipulation
    def loadJson(self):
        try:
            with open(self.filepath, "r") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print(f"The file at '{self.filepath}' could not be found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    # Method to be inherited and used in other files that organize json files in a readable format
    def dumpsJson(self):
        try:
            with open(self.filepath, "r") as json_file:
                return json_file.read()
        except FileNotFoundError:
            print(f"The file at '{self.filepath}' could not be found.")
        except Exception as e:
            print(f"An error occurred: {e}")

# Test Class
# print(JsonObjectConstructor('src/testdata/ddAllertsPayload1.json').dumpsJson())
    