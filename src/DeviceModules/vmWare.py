#Author Ben Meyers
import urllib3
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import dotenv
import requests
import os
from DeviceModules import classes
import json
import atexit
import ssl


# Start session a disable certifcate verification
session = requests.session()
session.verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Get the capacity data with the pyvmomi sdk
def get_capacity_data(service_instance):
    info = {}
    content = service_instance.RetrieveContent()

    # Get datastore information
    datastore_info = []
    datastore_container = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datastore], True)
    datastores = datastore_container.view
    # Get datastore information
    for datastore in datastores:
        capacity = datastore.summary.capacity / (1024**3)
        free_space = datastore.summary.freeSpace / (1024**3)
        used_space = (datastore.summary.capacity - datastore.summary.freeSpace) / (1024**3)
        datastore_data = {
            "Name" : datastore.summary.name,
            "Type" : datastore.summary.type,
            "Accessible" : datastore.summary.accessible,
            'capacity_rounded': round(capacity, 2),
            "Capacity_GB": format(capacity, '.2f') + ' GB',
            'free_space_rounded': round(free_space, 2),
            "Free_Space_GB": format(free_space, '.2f') + ' GB',
            "Used_Space_GB": format(used_space, '.2f') + ' GB',
            "Free_Space_Percent": format(free_space / capacity * 100, '.2f') + ' %',
            "Used_Space_Percent": format(used_space / capacity * 100, '.2f') + ' %'
        }
        datastore_info.append(datastore_data)
    return datastore_info

def get_report(device: classes.Device, report: classes.Report):
    # Load vCenter env variables
    vcenter_apihost = device.hostname
    vcenter_username = device.username
    vcenter_password = device.password

    # Create ssl context
    context = None
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Connect to the vCenter server
    si = SmartConnect(host=vcenter_apihost, user=vcenter_username, pwd=vcenter_password, sslContext=context)
    content = si.RetrieveContent()
    datastore_raw_data = get_capacity_data(si)
    atexit.register(Disconnect, si)
    # test_vsphere_automation()
    datastore_payload_data = []
    for datastore in datastore_raw_data:
        datastore_payload_data.append({
            'name' : datastore['Name'],
            'capacity': datastore['capacity_rounded'],
            'freespace': datastore['free_space_rounded'],
            'type' : datastore["Type"]
        })
        report.rows.append([datastore["Name"],datastore["Type"],datastore["Capacity_GB"],datastore["Free_Space_GB"],datastore["Used_Space_GB"],datastore["Used_Space_Percent"],datastore["Free_Space_Percent"],datastore["Accessible"]])
    report.dictData=datastore_payload_data
    return report