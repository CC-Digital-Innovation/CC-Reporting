import requests
import json
from loguru import logger
from config import classes
import csv

GB = ((1/1024)/1024)

#Get Auth token
def ddauth(ip, creds, headers):
        #first post to auth endoing
        logger.info('Getting auth token for Data Domain API')
        auth = requests.post(f'https://{ip}:3009/rest/v1.0/auth' , headers=headers, data = json.dumps(creds), verify =False)
        logger.debug(f'authentication reponse code: {auth}')
        return auth.headers['X-DD-AUTH-TOKEN']


def get_capacity(ip, creds, headers):
        #add response token to headers
        headers['X-DD-AUTH-TOKEN']=ddauth(ip, creds, headers)
        logger.info('Using token to get system capacity data')
        #now we can get from capacity endpoint
        system = requests.get(f'https://{ip}:3009/rest/v1.0/system' , headers=headers, verify =False)
        logger.debug(f'system response code: {system}')

        #calc data from endpoint, normalize to Gigabytes
        logger.info('Calculating results')
        used = (float(system.json()['physical_capacity']['used'])*GB)/1024
        total = (float(system.json()['physical_capacity']['total'])*GB)/1024
        free = (float(system.json()['physical_capacity']['available'])*GB)/1024

        return classes.StorageDevice(round(used, 3), round(total, 3), GB, round(free, 3))

def get_alerts(ip, creds, headers):
        
        #add response token to headers
        headers['X-DD-AUTH-TOKEN']=ddauth(ip, creds, headers)
        #get active alerts
        alertslist = []
        alertsstr = ''
        for alert in alertslist:
                tempstring = f"{alert['severity']}: {alert['description']}\n"
                alertsstr = alertsstr + tempstring
                alertslist.append(tempstring)
        return {"alerts" : alertslist, "str" : alertsstr}


def get_report(device: classes.Device, report: classes.Report):
        headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                }
        creds = {"username":device.username, "password": device.password}
        caps = get_capacity(device.ip, creds, headers)
        #alerts = get_alerts(device.ip, creds, headers)
        # alerts['alerts'].len(), alerts['str']
        row = [caps.used_storage, caps.total_storage, caps.free_storage,"alert data here", "alert data here"]
        curr_rows = report.rows
        report.rows = curr_rows.append(row)
        return report

