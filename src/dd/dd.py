from dataclasses import dataclass
from typing import List
from openJson import JsonFileReader

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
class baseDict:
    id : str
    alert_id : str
    object_id : str
    event_id : str
    name : str
    alert_gen_epoch : int
    clear_epoch : int
    msg : str
    additional_info : str
    clear_additional_info : str
    status : str
    class_ : str
    severity : str
    action : str
    description : str
    node_id : int
    snmp_notification_oid : str
    link : List[Link]

    @classmethod
    def from_dict(cls, data):
        snmp_notification_oid = data.pop('snmp_notification_oid', None)
        object_id = data.pop('object_id', None)
        if object_id is not None:
            data['object_id'] = object_id
        else:
            data['object_id'] = None
        if snmp_notification_oid is not None:
            data['snmp_notification_oid'] = snmp_notification_oid
        else:
            data['snmp_notification_oid'] = None
        data['link'] = [Link.from_dict(link) for link in data['link']]
        data['class_'] = data.pop('class')
        return cls(**data)
        # data['class_'] = data.pop('class')
        # data['link'] = [Link.from_dict(link) for link in data['link']]

        # return cls(**data)
    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'object_id': self.object_id,
            'event_id': self.event_id,
            'name': self.name,
            'alert_gen_epoch': self.alert_gen_epoch,
            'clear_epoch': self.clear_epoch,
            'msg': self.msg,
            'additional_info': self.additional_info,
            'clear_additional_info': self.clear_additional_info,
            'status': self.status,
            'class': self.class_,
            'severity': self.severity,
            'action': self.action,
            'description': self.description,
            'node_id': self.node_id,
            'snmp_notification_oid': self.snmp_notification_oid,
            'link': [link.to_dict() for link in self.link],
        }


@dataclass
class alertList:
    alert_list: List[dict]

    @classmethod
    def from_dict(cls, data):
        data['alert_list'] = [baseDict.from_dict(alert) for alert in data['alert_list']]
        return cls(**data)
    def to_dict(self):
        return {
            'alert_list': [alert.to_dict() for alert in self.alert_list],
        }
    
json_file_reader = JsonFileReader('ddAllertsPayload.json')
jsonDat = json_file_reader.json_data
ddObject = alertList.from_dict(jsonDat)

if __name__ == '__main__':
    print(ddObject)
 