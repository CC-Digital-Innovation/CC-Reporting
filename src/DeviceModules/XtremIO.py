import requests
import json
from loguru import logger
from config import classes

GB = ((1/1024)/1024)


def get_capacity(device: classes.Device):
    #initialize REST header and device data
    headers = {
        'Content-Type': 'application/json'
    }

    #Get and parse results from xtremio clusters endpoint
    logger.info('Getting cluster data from XtremIO API')
    r = requests.get(f'https://{device.ip}/api/json/v3/types/clusters/1', auth=(device.username, device.password), headers=headers, verify =False)
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