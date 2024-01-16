import requests
import json
from loguru import logger
from src import storage_device

GB = ((1/1024)/1024)

# creds looks like {"username":USERNAME, "password": PASSWORD}
def get_capacity(creds, ip):
        headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                }
        #first post to auth endoing
        logger.info('Getting auth token for Data Domain API')
        auth = requests.post(f'https://{ip}:3009/rest/v1.0/auth' , headers=headers, data = json.dumps(creds), verify =False)
        logger.debug(f'authentication reponse code: {auth}')
        #add response token to headers
        headers['X-DD-AUTH-TOKEN']=auth.headers['X-DD-AUTH-TOKEN']
        logger.info('Using token to get system capacity data')
        #now we can get from capacity endpoint
        system = requests.get(f'https://{ip}:3009/rest/v1.0/system' , headers=headers, verify =False)
        logger.debug(f'system response code: {system}')

        #calc data from endpoint, normalize to Gigabytes
        logger.info('Calculating results')
        used = (float(system.json()['physical_capacity']['used'])*GB)/1024
        total = (float(system.json()['physical_capacity']['total'])*GB)/1024
        free = (float(system.json()['physical_capacity']['available'])*GB)/1024

        return storage_device.StorageDevice(round(used, 3), round(total, 3), GB, round(free, 3))