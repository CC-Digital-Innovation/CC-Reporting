from dataclasses import dataclass
from openJson import JsonFileReader

# Extrapolate base structure into callable class object for data validation, storage, and retrieval accross multiple files
@dataclass
class baseDict:
    category : str
    code : int
    actual : None
    opened : str
    component_type : str
    id : int
    current_severity : str
    details : str
    expected : None
    event : str
    component_name : str

    @classmethod
    def from_dict_list(cls, list_of_data):
        return [cls(**data) for data in list_of_data]
    def to_dict(self):
        return {
            'category': self.category,
            'code': self.code,
            'actual': self.actual,
            'opened': self.opened,
            'component_type': self.component_type,
            'id': self.id,
            'current_severity': self.current_severity,
            'details': self.details,
            'expected': self.expected,
            'event': self.event,
            'component_name': self.component_name
        }

        
    
json_file_reader = JsonFileReader('pureAlert.json')
jsonDat = json_file_reader.json_data
pureObject = baseDict.from_dict_list(jsonDat)
