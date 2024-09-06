import requests
import json
from loguru import logger
from config import classes

GB = ((1/1024)/1024)


def get_capacity(ip, usr, passw, head):
    #initialize REST header and device data

    #Get and parse results from xtremio clusters endpoint
    logger.info('Getting cluster data from XtremIO API')
    r = requests.get(f'https://{ip}/api/json/v3/types/clusters/1', auth=(usr, passw), headers=head, verify =False)
    logger.debug(f'API response code: {r}')
    total = r.json()['content']['ud-ssd-space']
    totuse = r.json()['content']['logical-space-in-use']
    reduc  = r.json()['content']['data-reduction-ratio']

    #calc percentages and free space
    logger.info('Calculating XtremIO report from raw data')
    used = float(totuse)/float(reduc)
    free=float(total)-used

    #calls helper function to make dictionary and adds to running list
    logger.info('Compiling data into dictionary')

    return classes.StorageDevice(round(used, 3), round(total, 3), GB, round(free, 3))

def get_alerts(ip, usr, passw , head):
        r = requests.get(f'https://{ip}/api/json/v3/types/alerts', auth=(usr, passw), headers=head, verify =False)
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
            'Content-Type': 'application/json'
        }
        caps = get_capacity(device.ip, device.username, device.password, headers)
        alerts = get_alerts(device.ip, device.username, device.password, headers)
        row = [caps.used_storage, caps.total_storage, caps.free_storage, alerts['str'], len(alerts['alerts'])]
        curr_rows = report.rows
        report.rows = curr_rows.append(row)
        return report
