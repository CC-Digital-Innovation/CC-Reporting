#Author Ben Meyersimport requests
import urllib3
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import dotenv
import requests
import os
import json
import atexit
import ssl
from vmware.vapi.vsphere.client import create_vsphere_client

# Load NocDB env variables
dotenv.load_dotenv()
nocodb_url = os.getenv("nocodb_url")
xc_auth = os.getenv("nocodb_xcauth")

# Start session a disable certifcate verification
session = requests.session()
session.verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get NocoDB data from their REST API
def get_nocodb_data():
    headers = {
        'xc-auth': xc_auth
    }
    response = requests.get(nocodb_url, headers=headers)
    if response.status_code != 200:
        return {"error": "Error getting NocoDB data"}
    else:
        return response.text

# Parse the NocoDB data
def get_parsed_nocodb_data(data):
    try:
        data = json.loads(data)
        envvariable_names = []
        envvariable_values = []
        for i in data["list"]:
            if i["enviornment variables"] != None:
                envvariable_names.append(i["enviornment variables"])
            if i["values"] != None:
                envvariable_values.append(i["values"])
        return envvariable_names, envvariable_values
    except:
        return {"error": "Error parsing NocoDB data"}

# Structure the enviornment variables from the nocodb cloud table into a dictionary
def get_allenv_variables():
    env_names, env_values = get_parsed_nocodb_data(get_nocodb_data())
    # Make a dictionary of each env_name to env_value
    env_dict = {}
    for i in range(len(env_names)):
        env_dict[env_names[i]] = env_values[i]
    return env_dict

# Load NocDB env variables
config = get_allenv_variables()

# Load vCenter env variables
vcenter_apihost = config["vcenter_apihost"]
vcenter_username = config["vcenter_username"]
vcenter_password = config["vcenter_password"]

# Create ssl context
context = None
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Connect to the vCenter server
si = SmartConnect(host=vcenter_apihost, user=vcenter_username, pwd=vcenter_password, sslContext=context)
content = si.RetrieveContent()

# Get the capacity data with the pyvmomi sdk
def get_capacity_data(service_instance):
    info = {}
    content = service_instance.RetrieveContent()

    # Get datastore information
    datastore_info = {}
    datastore_container = content.viewManager.CreateContainerView(content.rootFolder, [vim.Datastore], True)
    datastores = datastore_container.view
    # Get datastore information
    for datastore in datastores:
        capacity = datastore.summary.capacity / (1024**3)
        free_space = datastore.summary.freeSpace / (1024**3)
        used_space = (datastore.summary.capacity - datastore.summary.freeSpace) / (1024**3)
        datastore_info[datastore.name] = {
            "Capacity_GB": format(capacity, '.2f') + ' GB',
            "Free_Space_GB": format(free_space, '.2f') + ' GB',
            "Used_Space_GB": format(used_space, '.2f') + ' GB',
            "Free_Space_Percent": format(free_space / capacity * 100, '.2f') + ' %',
            "Used_Space_Percent": format(used_space / capacity * 100, '.2f') + ' %'
        }
    info["Datastore_Storage_Info"] = datastore_info
    # Get memory information for each ESXi host
    memory_info = {}
    host_container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = host_container.view
    # Get memory information for each ESXi host
    for host in hosts:
        total_memory = host.hardware.memorySize / (1024**3)
        used_memory = (host.hardware.memorySize - host.summary.quickStats.overallMemoryUsage) / (1024**3)
        free_memory = host.summary.quickStats.overallMemoryUsage / (1024**3)
        free_memory_percent = (host.summary.quickStats.overallMemoryUsage / host.hardware.memorySize) * 100
        memory_info[host.name] = {
            "Total_Memory_GB": format(total_memory, '.2f') + ' GB',
            "Used_Memory_GB": format(used_memory, '.2f') + ' GB',
            "Free_Memory_GB": format( free_memory, '.2f') + ' GB',
            "Free_Memory_Percent": format(free_memory_percent, '.2f') + ' %'
        }
    info["Host_Memory_Info"] = memory_info
    # Get CPU information for each ESXi host
    cpu_info = {}
    for host in hosts:

        cpu_info[host.name] = {
            "Total_CPU_Cores": host.hardware.cpuInfo.numCpuCores,
            "Total_CPU_Threads": host.hardware.cpuInfo.numCpuThreads,
        }
    info["CPU_Info"] = cpu_info
    datastore_container.Destroy()
    host_container.Destroy()

    # Get Memory information from each VM
    vm_info = {}
    vm_container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    vms = vm_container.view
    for vm in vms:
        total_memory = vm.summary.config.memorySizeMB / 1024
        used_memory = vm.summary.quickStats.guestMemoryUsage / 1024
        free_memory = total_memory - used_memory
        used_memory_percent = (used_memory / total_memory) * 100
        free_memory_percent = 100 - used_memory_percent
        vm_info[vm.name] = {
            "Total_Memory_GB": format(total_memory, '.2f') + ' GB',
            "Used_Memory_GB": format(used_memory, '.2f') + ' GB',
            "Free_Memory_GB": format(free_memory, '.2f') + ' GB',
            "Used_Memory_Percent": format(used_memory_percent, '.2f') + ' %',
            "Free_Memory_Percent": format(free_memory_percent, '.2f') + ' %'
        }
    info["VM_Info"] = vm_info
    vm_container.Destroy()
    return info
# # Get all the alarms
def get_alarms(service_instance):
    content = service_instance.RetrieveContent()
    lis_of_alarms = []
    for ta in content.rootFolder.triggeredAlarmState:
        alarm_dict = {
            'alarm_name': ta.alarm.info.name,
            'entity_name': ta.entity.name,
            'alarm_key': ta.alarm.info.key,
            'alarm_description': ta.alarm.info.description,
            'object': ta.entity.name,
            'time': str(ta.time),
            'overall_status': ta.overallStatus,
            'acknowledged': ta.acknowledged,
            'acknowledged_time': str(ta.acknowledgedTime),
            'acknowledged_by_user': ta.acknowledgedByUser,
        }
        lis_of_alarms.append(alarm_dict)
    return lis_of_alarms

if __name__ == "__main__":
    print(json.dumps(get_alarms(si), indent=4, sort_keys=True))
    print(json.dumps(get_capacity_data(si), indent=4, sort_keys=True))
    atexit.register(Disconnect, si)
    # test_vsphere_automation()




















