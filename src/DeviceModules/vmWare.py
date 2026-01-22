import atexit
import ssl
from dataclasses import asdict, dataclass, field
from datetime import datetime

import requests
import urllib3
from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim

from DeviceModules import classes

# Start session a disable certifcate verification
session = requests.session()
session.verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Get the capacity data with the pyvmomi sdk
def get_capacity_data(service_instance):
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
        vms = len(datastore.vm)
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
            "Used_Space_Percent": format(used_space / capacity * 100, '.2f') + ' %',
            "vmcount" : vms
        }
        datastore_info.append(datastore_data)
    return datastore_info

def query_performance_manager(content, samples, host, statId, inst = "", interval = None):
    performanceManager = content.perfManager
    metricId = vim.PerformanceManager.MetricId(counterId = statId, instance= inst)
    query = vim.PerformanceManager.QuerySpec(intervalId = interval, maxSample = samples, entity=host, metricId=[metricId])
    perfResults = performanceManager.QueryPerf(querySpec=[query])
    return perfResults

def get_perf_metrics(service_instance):
    content = service_instance.RetrieveContent()
    #Create counterid map for performance stats
    id_map = {}
    id_list = content.perfManager.perfCounter
    for id in id_list:
        stat_name = f"{id.groupInfo.key}.{id.nameInfo.key}.{id.rollupType}"
        id_map[stat_name] = id.key
    # Get performance information from each ESXi host
    host_container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = host_container.view
    performance_info = []
    for host in hosts:
        cpuready = query_performance_manager(content, 1, host, id_map["cpu.ready.summation"], interval =20)
        memballoon = query_performance_manager(content, 1, host, id_map["mem.vmmemctl.average"], interval =20)
        memswapped = query_performance_manager(content, 1, host, id_map["mem.swapused.average"], interval =20)
        networkTP = query_performance_manager(content, 5, host, id_map["net.usage.average"], interval = 20)
        readLat = query_performance_manager(content, 3, host, id_map["datastore.totalReadLatency.average"], inst = "*", interval=20)
        writeLat = query_performance_manager(content, 3, host, id_map["datastore.totalWriteLatency.average"], inst = "*", interval=20)
        name = host.name
        readLatAvg = sum(readLat[0].value[0].value)/len(readLat[0].value[0].value)
        writeLatAvg = sum(writeLat[0].value[0].value)/len(writeLat[0].value[0].value)
        disklat = (readLatAvg+writeLatAvg)/2
        mb_memball = round((float(memballoon[0].value[0].value[0])/1024), 2)
        mb_memswap = round((float(memswapped[0].value[0].value[0])/1024), 2)
        cpuready_perc = round((float(cpuready[0].value[0].value[0])/20000)*100, 2)
        network_throughput = round(((sum(networkTP[0].value[0].value)/len(networkTP[0].value[0].value)))/1024, 2)
        powerStatus = host.runtime.powerState
        connectionStatus = host.runtime.connectionState
        cpuPercent = (host.summary.quickStats.overallCpuUsage)/(host.summary.hardware.numCpuCores*(host.summary.hardware.cpuMhz))*100
        cputotal = host.summary.hardware.numCpuCores*(host.summary.hardware.cpuMhz/1000)
        memPercent = (host.summary.quickStats.overallMemoryUsage)/((host.summary.hardware.memorySize/1000000))*100
        memtotal = (host.hardware.memorySize/1000000000)
        uptime = host.summary.quickStats.uptime/60/60/24
        vmcount = len(host.vm)
        numcpus = host.summary.hardware.numCpuCores
        vcputotal=0
        for vm in host.vm:
            if vm.summary.runtime.powerState == 'poweredOn':
                vcputotal=vcputotal+vm.summary.config.numCpu
        vcpuratio = round(vcputotal/numcpus, 2)
        model = host.summary.hardware.model
        version = host.summary.config.product.version
        status = 'Good'
        if(cpuPercent>90 or memPercent>85):
            status = 'Critical'
        elif(cpuPercent>70 or memPercent>70):
            status = 'Warning'

        performance_data= {
            'name' : name,
            'powerStatus': powerStatus,
            'connectionStatus' : connectionStatus,
            'cpuPercent' : cpuPercent,
            'cpuTotal' : cputotal,
            'memPerfcent' : memPercent,
            'memtotal' :  memtotal,
            'uptime' : uptime,
            'vmcount' : vmcount,
            'numCpus' : numcpus,
            'model' : model,
            'version' : version,
            'status' : status,
            'disklat' : disklat,
            'mem_balloon': mb_memball,
            'mem_swap' : mb_memswap,
            'cpuready' : cpuready_perc,
            'networkTp' : network_throughput,
            'vcputotal' : vcputotal,
            'vcpuratio' : vcpuratio
        }
        performance_info.append(performance_data)
    host_container.Destroy()
    return performance_info

def get_licenses(content: vim.ServiceInstanceContent):
    lm = content.licenseManager.licenseAssignmentManager
    licenses = []

    # get vcenter licenses
    vcenter_license_assignments = lm.QueryAssignedLicenses(content.about.instanceUuid)
    licenses.extend(License.from_license_assignment(la) for la in vcenter_license_assignments)

    # get esxi host licenses
    host_container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = host_container.view
    for h in hosts:
        host_license_assignments = lm.QueryAssignedLicenses(h._moId)
        licenses.extend(License.from_license_assignment(la) for la in host_license_assignments)
    host_container.Destroy()

    return licenses


@dataclass
class License:
    """
    custom dataclass to flatten pyvmomi's LicenseInfo class
    """
    name: str
    entity_name: str
    product_name: str
    product_version: str
    file_version: str
    expiration_date: datetime | None = None
    features: list[str] = field(default_factory=list)

    @classmethod
    def from_license_assignment(cls, license: vim.LicenseAssignmentManager.LicenseAssignment):
        # default attribute values in case properties are missing
        product_name = ''
        product_version = ''
        file_version = ''
        expiration_date = None
        features = []

        # loop through properties (stored as list of custom key-value object)
        for p in license.assignedLicense.properties:
            if p.key == 'ProductName':
                product_name = p.value
            elif p.key == 'ProductVersion':
                product_version = p.value
            elif p.key == 'FileVersion':
                file_version = p.value
            elif p.key == 'expirationDate':
                expiration_date = p.value
            elif p.key == 'feature':
                features.append(p.value.value)

        return cls(
            name = license.assignedLicense.name,
            entity_name = license.entityDisplayName or '',
            product_name = product_name,
            product_version = product_version,
            file_version = file_version,
            expiration_date = expiration_date,
            features = features)

    def to_json(self):
        data = asdict(self)
        # convert datetime to str
        if data['expiration_date'] is not None:
            data['expiration_date'] = str(data['expiration_date'])
        return data


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
    perf_metrics = get_perf_metrics(si)
    licenses = get_licenses(content)
    atexit.register(Disconnect, si)
    # test_vsphere_automation()
    datastore_payload_data = []
    for datastore in datastore_raw_data:
        datastore_payload_data.append({
            'name' : datastore['Name'],
            'capacity': datastore['capacity_rounded'],
            'freespace': datastore['free_space_rounded'],
            'type' : datastore["Type"],
            'vmcount' : datastore['vmcount']
        })
        report.rows.append([datastore["Name"],datastore["Type"],datastore["Capacity_GB"],datastore["Free_Space_GB"],datastore["Used_Space_GB"],datastore["Used_Space_Percent"],datastore["Free_Space_Percent"],datastore["Accessible"]])
    
    report.dictData={'datastore_Cap' : datastore_payload_data, 
                     'vm_performance' : perf_metrics,
                     'licenses': [l.to_json() for l in licenses]}
    return report