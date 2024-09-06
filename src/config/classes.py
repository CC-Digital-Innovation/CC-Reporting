from pydantic import BaseModel
from dataclasses import dataclass
import csv

class Alert(BaseModel):
    """
    Represents an alert that exists on a machine.

    Members:
        description (str): The description of the alert.
        affected_device (str): The device with the alert.
        severity (str): The severity of the alert.
    """

    description: str
    affected_device: str
    severity: str


@dataclass
class StorageDevice:
    """Class to store storage device data"""
    used_storage: float
    total_storage: float
    unit_of_measurement: str
    free_storage   : float

    def get_utilization_percentage(self, decimal_precision: int) -> float:
        return round(self.used_storage / self.total_storage, decimal_precision)

class Report:
    rows: list[list]
    csvData: str
    dictData: dict
    headerRow: list

    def __init__(self, headerrow):
        self.headerRow = headerrow
        self.rows = []

    def makecsv():
        pass
    def makedict():
        pass


class Device:
    """Class to store Device information to easily pass along to other functions"""
    snowname: str
    username: str = None
    password: str = None
    ip:       str = None
    vmaxsid:  str = None
    snowdata: dict = None
    type: str = None

    def __init__(self, name, data, type):
        self.snowname = name
        self.snowdata = data
        self.type = type
        self.username = data['username'] #placeholder
        self.password = data['password'] #placeholder
        self.ip       = data['ip'] #placeholder
        self.vmaxsid  = data['serialnum'][-3:] #placeholder

    
