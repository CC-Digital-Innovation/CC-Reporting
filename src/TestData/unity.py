from dataclasses import dataclass
from typing import List, Optional
from openJson import JsonFileReader

# Dataclasses for Unity payload to be validate data and store data accross multiple files
@dataclass
class Link:
    rel: str
    href: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return {'rel': self.rel, 'href': self.href}


@dataclass
class Component:
    id: str
    resource: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return {'id': self.id, 'resource': self.resource}

@dataclass
class Content:
    content_id: str
    severity: int
    state: int
    timestamp: str
    component: Optional[Component]  # Use Optional from typing
    message: str
    description: str

    @classmethod
    def from_dict(cls, data):
        component_data = data.pop('component', None)
        data['content_id'] = data.pop('id') 
        if component_data is not None:
            data['component'] = Component.from_dict(component_data)
        else:
            data['component'] = None  # Set component to None if it's not present
        return cls(**data)

    def to_dict(self):
        result = {
            'id': self.id,
            'severity': self.severity,
            'state': self.state,
            'timestamp': self.timestamp,
            'message': self.message,
            'description': self.description,
        }

        if self.component is not None:
            result['component'] = self.component.to_dict()

        return result
@dataclass
class EntryList:
    base: str
    updated: str
    links: List[Link]
    content: Content

    @classmethod
    def from_dict(cls, data):
        data['links'] = [Link.from_dict(link) for link in data['links']]
        data['content'] = Content.from_dict(data['content'])
        data['base'] = data.pop('@base')  # Rename '@base' to 'base'
        return cls(**data)

    def to_dict(self):
        return {
            '@base': self.base,
            'updated': self.updated,
            'links': [link.to_dict() for link in self.links],
            'content': self.content.to_dict(),
        }


@dataclass
class BaseClass:
    base: str
    updated: str
    links: List[Link]
    entries: List[EntryList]

    @classmethod
    def from_dict(cls, data):
        data['links'] = [Link.from_dict(link) for link in data['links']]
        data['base'] = data.pop('@base')  # Rename '@base' to 'base'
        data['entries'] = [EntryList.from_dict(entry) for entry in data['entries']]
        return cls(**data)

    def to_dict(self):
        return {
            '@base': self.base,
            'updated': self.updated,
            'links': [link.to_dict() for link in self.links],
            'entries': [entry.to_dict() for entry in self.entries],
        }

# Create objects
filepath = "unityAlert.json"
json_instance = JsonFileReader(filepath)
jsonDat = json_instance.json_data
unityObject = BaseClass.from_dict(jsonDat)

if __name__ == '__main__':
    print(unityObject)