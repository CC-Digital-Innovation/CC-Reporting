import requests
import json
from loguru import logger
from config import classes

GB = ((1/1024)/1024)

def make_session(ip, payload, header):
    #set header and credentials for session auth
    
    #get token
    logger.info('Getting api token for Pure API session')
    auth = requests.post(f'https://{ip}/api/1.17/auth/apitoken', data = json.dumps(payload), headers = header, verify = False)
    logger.debug(f"auth reponse code: {auth}")

    #init session
    logger.info('starting Pure API session')
    sess = requests.Session()
    s = sess.post(f'https://{ip}/api/1.17/auth/session', data = json.dumps(auth.json()), headers = header, verify = False)
    logger.debug(f'Session reponse code: {s}')
    return sess

def get_capacity(ip, payload, header):
    sess = make_session(ip, payload, header)

    #get array capacity values
    logger.info('Getting data from capacity and disk API endpoints')
    array = sess.get(f'https://{ip}/api/1.17/array?space=true', headers = header, verify = False)
    logger.debug(f'Array reponse code: {array}')


    #calculate and normalize data for csv
    logger.info('Calculating Pure report from raw data and checking for disk failures')
    capdata = array.json()[0]
    used = round((capdata['snapshots'] + capdata['volumes'] + capdata['shared_space'])*(GB/1024),3)
    total = round(capdata['capacity']*(GB/1024),3)
    free = round(total-used, 3)
    return classes.StorageDevice(round(used, 3), round(total, 3), GB, round(free, 3))

def get_alerts(ip, payload, header):
        sess = make_session(ip, payload, header)
        #get active alerts
        alertslist = []
        alertsstr = ''
        for alert in alertslist:
                tempstring = f"{alert['current_severity']}: {alert['event']} in {alert['component']}\n"
                alertsstr = alertsstr + tempstring
                alertslist.append(tempstring)
        return {"alerts" : alertslist, "str" : alertsstr}


def get_report(device: classes.Device, report: classes.Report):
    header = {
        'Content-Type': 'application/json'
    }
    payload = {
        'username' : device.username,
        'password' : device.password
    }
    caps = get_capacity(device.ip, payload, header)
    #alerts = get_alerts(device.ip, payload, header)
    row = [caps.used_storage, caps.total_storage, caps.free_storage,"alert data here", "alert data here"]
    if report.rows:
            report.rows = report.rows.append(row)
    else:
            report.rows = [row]
    return report