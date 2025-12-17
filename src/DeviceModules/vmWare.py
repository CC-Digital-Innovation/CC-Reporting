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

def query_performance_manager(content, samples, host, statId):
    performanceManager = content.perfManager
    metricId = vim.PerformanceManager.MetricId(counterId = statId)
    query = vim.PerformanceManager.QuerySpec(maxSample = samples, entity=host, metricId=[metricId])
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
        cpuready = query_performance_manager(content, 1, host, "cpu.ready.summation")
        memballoon = query_performance_manager(content, 1, host, "mem.vmmemctl.average")
        memswapped = query_performance_manager(content, 1, host, "mem.swapused.average")
        networkTP = query_performance_manager(content, 5, host, "net.usage.average")
        dstores = host.datastore
        readLatTotal = 0
        writeLatTotal = 0
        for dstore in dstores:
            readLat = query_performance_manager(content, 3, dstore, "datastore.totalReadLatency.average")
            writeLat = query_performance_manager(content, 1, dstore, "datastore.totalWriteLatency.average")
            readLatTotal = readLatTotal + readLat
            writeLatTotal = writeLatTotal + writeLat
        avgReadLat = readLatTotal/len(dstore)
        avgwriteLat = writeLatTotal/len(dstore)
        name = host.name
        powerStatus = host.runtime.powerState
        connectionStatus = host.runtime.connectionState
        cpuPercent = (host.summary.quickStats.overallCpuUsage)/(host.summary.hardware.numCpuCores*(host.summary.hardware.cpuMhz))*100
        cputotal = host.summary.hardware.numCpuCores*(host.summary.hardware.cpuMhz/1000)
        memPercent = (host.summary.quickStats.overallMemoryUsage)/((host.summary.hardware.memorySize/1000000))*100
        memtotal = (host.hardware.memorySize/1000000000)
        uptime = host.summary.quickStats.uptime/60/60/24
        vmcount = len(host.vm)
        numcpus = host.summary.hardware.numCpuCores
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
            'status' : status
        }
        performance_info.append(performance_data)
    host_container.Destroy()
    return performance_info

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
    
    report.dictData={'datastore_Cap' : datastore_payload_data, 'vm_performance' : perf_metrics}
    return report