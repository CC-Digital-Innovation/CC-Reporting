from pydantic import BaseModel
from dataclasses import dataclass


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
    capacity: list[list]
    alerts: list[list]
    replications: list[list]
    directors: list[list]
    hardware: list[list]
    faileddisk: list[list]
    snapshots: list[list]
    rows: list[list]
    devices: list
    csvData: str
    dictData: dict
    headerRow: list

    def __init__(self, headerrow):
        self.headerRow = headerrow
        self.rows = []

    def output_csv(self) -> list[list[str]]:
        # Make the output CSV and insert the header row.
        csv_table = list[str]()
        csv_table.append(self.headerRow)
        
        # Add each row as a string seperating data with commas.
        for row in self.rows:
            csv_table.append(','.join(row))

        return csv_table
        
    def output_data_as_dicts(self) -> list[dict[str, str]]:
        # For each row of data, turn it into a dictionary.
        all_data = list[dict[str, str]]()
        for row in self.rows:
            # Add each element of the data with its corresponding key from the header row.
            current_item = {}
            for header_index,element in enumerate(row):
                current_item[self.headerRow[header_index]] = element
            
            # Add the dictionary of data to the return list.
            all_data.append(current_item)
        
        return all_data


class Device:
    """Class to store Device information to easily pass along to other functions"""
    snowname: str
    hostname: str
    username: str = None
    password: str = None
    ip:       str = None
    serial:  str = None
    snowdata: dict = None
    type: str = None

    def __init__(self, name, data, type):
        self.snowname = name
        self.snowdata = data
        self.type = type
        self.username = data['u_username'] 
        self.password = data['u_fs_password'] 
        self.serial  = data['serial_number'] 
        self.hostname = data['u_host_name']
        if len(data['ip_address'].split('//'))>1:
            self.ip  = data['ip_address'].split('//')[1].split(':')[0]
        else:
            self.ip  = data['ip_address'].split(':')[0]
