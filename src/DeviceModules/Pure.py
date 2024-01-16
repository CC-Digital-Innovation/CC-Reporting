import requests
import json
from loguru import logger
from src import storage_device

GB = ((1/1024)/1024)

# creds looks like {"username":USERNAME, "password": PASSWORD}
def get_capacity(usr, passw, ip):
    #set header and credentials for session auth
    header = {
        'Content-Type': 'application/json'
    }

    payload = {
        'username' : usr,
        'password' : passw
    }

    #get token
    logger.info('Getting api token for Pure API session')
    auth = requests.post(f'https://{ip}/api/1.17/auth/apitoken', data = json.dumps(payload), headers = header, verify = False)
    logger.debug(f"auth reponse code: {auth}")

    #init session
    logger.info('starting Pure API session')
    sess = requests.Session()
    s = sess.post(f'https://{ip}/api/1.17/auth/session', data = json.dumps(auth.json()), headers = header, verify = False)
    logger.debug(f'Session reponse code: {s}')

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
    return storage_device.StorageDevice(round(used, 3), round(total, 3), GB, round(free, 3))