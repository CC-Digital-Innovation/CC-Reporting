from dataclasses import dataclass
from typing import List

# Script to extract payload information into dataclass instances
# The project turns each payload into dataclass instance
# We can then use the dataclass instance to extract the information we need
# We can turn the data we need into dataclass instances
# We can then turn the dataclass instances back into a list of dictionaries
# We can then remove the duplicates from the list of dictionaries
# We can then turn the list of dictionaries back into a dataclass instance
# Class methods can be used to turn the dataclass instance into a dictionary 
# Regular methods can be used to turn the dataclass instance into a list of dictionaries

@dataclass
class ddStorageAlert:
    alert_id: str
    additional_info: str
    msg: str
    object_id: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'additional_info': self.additional_info,
            'msg': self.msg,
            'object_id': self.object_id,
        }
@dataclass
class ddDNSAlert:
    alert_id: str
    additional_info: str
    msg: str
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'additional_info': self.additional_info,
            'msg': self.msg,
        }
    
@dataclass
class pureAlert:
    component_name: str
    event: str
    current_severity: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'component_name': self.component_name,
            'event': self.event,
            'current_severity': self.current_severity,
        }
@dataclass
class pureSoftwareAlert:
    component_name: str
    event: str
    current_severity: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'component_name': self.component_name,
            'event': self.event,
            'current_severity': self.current_severity,
        }
@dataclass
class pureUpgradeAlert:
    component_name: str
    event: str
    current_severity: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'component_name': self.component_name,
            'event': self.event,
            'current_severity': self.current_severity,
        }

@dataclass
class unityPoolAlert:
    message: str
    id: str
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
        }
@dataclass
class unityFilesystemAlert:
    id: str
    message: str
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'content_id': self.id,
            'message': self.message,
        }

@dataclass
class unityBackupAlert:
    message: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'message': self.message,
        }
@dataclass
class unitySoftwareAlert:
    message: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'message': self.message,
        }
@dataclass
class unityHardwareAlert:
    message: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'message': self.message,
        }
@dataclass
class unitySuccessAlert:
    message: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'message': self.message,
        }
@dataclass
class nonUniqueObject:
    nonUniqueList: List

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'nonUniqueList': self.nonUniqueList,
        }
@dataclass
class uniqueObject:
    uniqueList: List

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def to_dict(self):
        return {
            'uniqueList': self.uniqueList,
        }
