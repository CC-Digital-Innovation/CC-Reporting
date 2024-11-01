from DeviceModules import Isilon, DataDomain, Pure, UCS, VMAX, XtremIO
from config import classes
from pathlib import PurePath
import dotenv
import tempfile
import os
import csv
import json
import sys
import pysnow
import configparser
import requests
from loguru import logger
import urllib3
urllib3.disable_warnings()

#Set up globals from .env
dotenv.load_dotenv(PurePath(__file__).with_name('.env'))
URL = os.getenv('EMAIL_API_URL')
EMAILAPI_TOKEN = os.getenv('EMAIL_TOKEN')
SNOW_INSTANCE = os.getenv('SNOW_INSTANCE')
SNOW_USERNAME = os.getenv('SNOW_USER')
SNOW_PASSWORD = os.getenv('SNOW_PASSWORD')
CMDB_PATH     = os.getenv('CMDB_PATH')

snow_client = pysnow.Client(instance=SNOW_INSTANCE, user=SNOW_USERNAME, password=SNOW_PASSWORD)


def query_Device(DeviceName):
    #Query client for Device by name
    table = snow_client.resource(api_path=CMDB_PATH)
    RPquery = (
        pysnow.QueryBuilder()
        .field('name').equals(DeviceName)
    )
    fetch = table.get(query=RPquery).all()

    #Check for results and decrypt password
    if fetch and fetch[0]:
        url = f"https://{SNOW_INSTANCE}.service-now.com/api/fuss2/ci_password/{fetch[0]['sys_id']}/getcipassword"
        header = {
            'Content-Type': 'application/json'
        }
        response = requests.get(url, auth=(SNOW_USERNAME, SNOW_PASSWORD), headers=header)
        json_data = response.text
        pwd_dict = json.loads(json_data)
        decrypted_password = pwd_dict['result']['fs_password']
        fetch[0]['u_fs_password']=decrypted_password

        return fetch[0]
    else:
        return None


def email_report(directory):
    uploadFiles = []
    table_titles = []
    for file in os.listdir(directory):
        logger.debug(f"Attatching {file}")
        table_titles.append(file.split(".")[0])
        uploadFiles.append(('files', open(os.path.join(directory, file), "rb")))

    Data = {
        'subject'     : os.getenv('SUBJECT'),
        'to'          : os.getenv('RECIPIENTS'),
        'cc'          : os.getenv('CC'),
        'bcc'         : os.getenv('BCC'),
        'report_name' : os.getenv('REPORTNAME'),
        'table_title' : table_titles
    }

    header = {
        'API_KEY' : EMAILAPI_TOKEN
    }

    r = requests.request("POST", url = URL, headers=header, data = Data, files=uploadFiles)
    logger.debug(r.json())
    
def logger_init():
    logger.remove()
    logger.add(sys.stderr, colorize=True, level="DEBUG")
    logger.info("*****************************")
    logger.info("*********Report Start********")
    logger.info("*****************************")


#Step 1: Get list of devices from noco - for now local list
logger_init()
#Step 2: get device data from snow - for now local list
with open(os.path.join("src", "devices.json"), "r") as devicefile:
    devicedata = json.load(devicefile)

#step 3: init device list with snow data
devicelist = []
for device in devicedata['devices']:
    if device['snowName']:
        logger.debug(f"Fetching snow data for {device['snowName']}")
        snowdevice = query_Device(device['snowName'])
        if snowdevice:
            devicelist.append(classes.Device(device['snowName'], snowdevice, device['type']))
#step 4: iterate over list of devices
    #get data from device module
    #aggregate data
module_map = {
        "DataDomain" : DataDomain,
        "Isilon"     : Isilon,
        #"Meraki"    : cisco_meraki,
        "Pure"       : Pure,
        "UCS"        : UCS,
        "VMAX"       : VMAX,
        "XtremIO"    : XtremIO
    }
reports = {
        "DataDomain" : classes.Report(['Name', 'Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
        "Isilon"     : classes.Report(['Name', 'Device', 'Alert Severity', 'Description']),
        "Meraki"     : classes.Report(['Name', 'Device', 'Alert Severity', 'Description']),
        "Pure"       : classes.Report(['Name', 'Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
        "UCS"        : classes.Report(['Name', 'Device', 'Alert Severity', 'Description']),
        "VMAX"       : classes.Report(['Name', 'Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
        "XtremIO"    : classes.Report(['Name', 'Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count'])
    }

for device in devicelist:
    if device.type in module_map.keys():
        logger.info(f"Starting report for {device.type}")
        try:
            reports[device.type] = module_map[device.type].get_report(device, reports[device.type])
        except Exception as e:
            logger.debug(e)

#step 5 make report from aggregated data
with tempfile.TemporaryDirectory() as csvdir:
    for key in reports.keys():
        temprep = reports[key]
        if temprep.rows:
            with open(os.path.join(csvdir, f"{key}.csv") , "w") as file:
                csvwrite = csv.writer(file)
                csvwrite.writerow(temprep.headerRow)
                csvwrite.writerows(temprep.rows)
    #step 6 email report with email api
    email_report(csvdir)