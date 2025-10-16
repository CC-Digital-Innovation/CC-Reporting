from DeviceModules import Isilon, DataDomain, Pure, UCS, VMAX, XtremIO
from DeviceModules import classes
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

#logger
def logger_init():
    logger.remove()
    logger.add(sys.stderr, colorize=True, level="DEBUG")
    logfile = os.path.join(os.getcwd(), 'latest.log')
    logger.add(logfile, level='DEBUG')
    logger.info("*****************************")
    logger.info("*********Report Start********")
    logger.info("*****************************")

logger_init()
#Set up globals from .env
dotenv.load_dotenv(PurePath(__file__).with_name('.env'))

SNOW_INSTANCE = os.getenv['Snow_Instance']
SNOW_USERNAME = os.getenv['Snow_User']
SNOW_PASSWORD = os.getenv['Snow_Password']
CMDB_PATH     = os.getenv['CMDB_Path']
DB_URL = os.getenv('DB_URL')
DB_HEADER = {
    "pscp_sec_token" : os.getenv('DB_TOKEN')
}
CUSTOMER = os.getenv("CUSTOMER_NAME")

def get_devices(custname):
    payload = json.dumps({
        "customer_name" : custname
    })
    r = requests.post(f"{DB_URL}", data = payload , headers=DB_HEADER)
    if r.status_code == 200:
        return r.json()["devices"]
    else:
        return {"Error" : "Error retrieving devices"}


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

    

#Step 1: Get list of devices from noco - for now local list
devicedata = get_devices(CUSTOMER)

devicelist = []
for device in devicedata:
    if device['cr61f_devicename']:
        #Step 2: get device data from snow - for now local list
        logger.debug(f"Fetching snow data for {device['cr61f_devicename']}")
        snowdevice = query_Device(device['cr61f_devicename'])
        #step 3: init device list with snow data
        if snowdevice:
            devicelist.append(classes.Device(device['cr61f_devicename'], snowdevice, device['cr61f_devicetype']))
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
    #step 6 save data back
    #save data back to dataverse
    