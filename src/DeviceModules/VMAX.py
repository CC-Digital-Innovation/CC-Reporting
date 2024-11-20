import os
import subprocess
import io
import requests
import time
import json
from loguru import logger
from DeviceModules import classes

GB = ((1/1024)/1024)

# cliname is defined in symcli configuration files. sid is last three digits of serial number
def get_capacity(ip, usr, passw, header, sn):
    now= int(time.time())*1000
    syms = requests.get(f'https://{ip}:8443/univmax/restapi/91/system/symmetrix', auth=(usr, passw), headers=header, verify =False)
    symid = ''
    for sym in syms.json()['symmetrixId']:
        if sym[-3:] == sn[-3:]:
            symid=sym
    thinPoolKeyParams = {
        "symmetrixId" : symid
    }
    r = requests.post(f'https://{ip}:8443/univmax/restapi/performance/ThinPool/keys', json=thinPoolKeyParams, auth=(usr, passw), headers=header, verify =False)
    usedsum=0.0
    totalsum=0.0
    freesum=0.0

    for pool in r.json()['poolInfo']:
        thinPoolParam = {
            "startDate" : now-300000, 
            "endDate" : now, 
            "symmetrixId" : symid, 
            "poolId" : pool['poolId'], 
            "metrics" : ["UsedPoolCapacity", "TotalPoolCapacity"] 
        }
        poolData= requests.post(f'https://{ip}:8443/univmax/restapi/performance/ThinPool/metrics', json=thinPoolParam, auth=(usr, passw), headers=header, verify =False)
        usedsum=usedsum+poolData.json()['resultList']['result'][-1]['UsedPoolCapacity']
        totalsum=totalsum+poolData.json()['resultList']['result'][-1]['TotalPoolCapacity']
    freesum=totalsum-usedsum
    
    return classes.StorageDevice(usedsum, totalsum, GB, freesum)


def get_alerts(ip, usr, passw , head):
        #get active alerts
        r = requests.get(f'https://{ip}:8443/univmax/restapi/91/system/alert?acknowledged=false&state=NEW&severity=CRITICAL&severity=FATAL', auth=(usr, passw), headers=head, verify =False)
        alertslist = []
        alertsstr = ''
        for alert in r.json()['alertId']:
            if alert:
                r3 = requests.get(f'https://{ip}:8443/univmax/restapi/91/system/alert/{alert}', auth=(usr, passw), headers=head, verify =False)
                tempstring = f"""{r3.json()['severity']}: {r3.json()['description']}
"""
                alertsstr = alertsstr + tempstring
                alertslist.append(tempstring)
        if alertsstr:
            return {"alerts" : alertslist, "str" : alertsstr.strip()}
        else:
            return {"alerts" : alertslist, "str" : "No Critical Unacknowledged Alerts"}


def get_report(device: classes.Device, report: classes.Report):
    headers = {
        'Content-Type': 'application/json'
    }
    caps = get_capacity(device.ip, device.username, device.password, headers, device.serial)
    alerts = get_alerts(device.ip, device.username, device.password, headers)
    if device.hostname:
        deviceName = device.hostname
    else:
        deviceName = device.snowname
    row = [deviceName, caps.used_storage, caps.total_storage, caps.free_storage, alerts['str'], len(alerts['alerts'])]
    if report.rows:
            report.rows = report.rows.append(row)
    else:
        report.rows = [row]
    return report