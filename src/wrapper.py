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


URL = os.getenv['Email_API_URL']
EMAILAPI_TOKEN = os.getenv['Email_API_Token']
SNOW_INSTANCE = os.getenv['Snow_Instance']
SNOW_USERNAME = os.getenv['Snow_User']
SNOW_PASSWORD = os.getenv['Snow_Password']
CMDB_PATH     = os.getenv['CMDB_Path']
NOCO_URL = os.getenv('NOCO_BASE_URL')
NOCO_DB_HEADER = {
    "xc-token" : os.getenv('NOCO_TOKEN')
}
NOCO_CONFIG_TABLE_ID = os.getenv("NOCO_CONFIG_TABLE_ID")
CUSTOMER = os.getenv("CUSTOMER_NAME")
def noco_config_retrieval(custname):
    search = {
        "where" : f"(Customer,eq,{custname})"
    }
    
    r = requests.get(f"{NOCO_URL}api/v2/tables/{NOCO_CONFIG_TABLE_ID}/records", params=search, headers=NOCO_DB_HEADER)
    logger.debug(f"Response from NoCo for config: {r}")
    if r.status_code == 200 and 'list' in r.json().keys():
        return r.json()['list'][0]
    else:
        logger.debug(f"Error getting config, response message{r.text}")
        return "Error retrieving configuration from NoCo"

def noco_get_devices(custname):
    r = requests.get(f"{NOCO_URL}api/v2/meta/bases/", headers=NOCO_DB_HEADER)
    if r.status_code == 200 and 'list' in r.json().keys():
        for customer in r.json()['list']:
            if customer['title']==custname:
                base = requests.get(f"{NOCO_URL}api/v2/meta/bases/{customer['id']}/tables", headers=NOCO_DB_HEADER)
                logger.debug(f"Response from NoCo for Customer table: {base}")
                if base.status_code == 200 and 'list' in base.json().keys():
                    for table in base.json()['list']:
                        if table['title'] == 'Devices':
                            devices=[]
                            page = 0
                            flag=True
                            while flag:
                                page = page +1
                                query= {"page":page}
                                repeat_request = requests.get(f"{NOCO_URL}api/v2/tables/{table['id']}/records", params =query, headers=NOCO_DB_HEADER)
                                logger.debug(f"Response from NoCo for devices: {repeat_request}")
                                if repeat_request.status_code == 200 and 'list' in repeat_request.json().keys():
                                    for device in repeat_request.json()['list']:
                                        devices.append(device)
                                    if r.json()['pageInfo']['isLastPage']:
                                        flag = False
                                else:
                                    logger.debug(f"Error getting devices, Noco Response message: {repeat_request.text}")
                                    return {"Error" : "Error retrieving devices"}
                            return devices
                    logger.debug(f"Customer Devices table not found")
                    return {"Error" : "Customer devices table not found"}
                else:
                    logger.debug(f"Error getting Customer table, Noco Response message: {base.text}")
                    return {"Error" : "Error retrieving base tables"}
        logger.debug(f"Customer table not found")
        return {"Error" : "customer table not found"}
    else:
        logger.debug(f"Error getting bases, Noco Response message: {r.text}")
        return {"Error" : "Error retrieving customer tables"}


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
    
    config = noco_config_retrieval(CUSTOMER)
    if config:
        pass
    else:
        raise Exception("Configuration retrieval failed")

    Data = {
        'subject'     : config['Email Subject'],
        'to'          : config['Email Recipients'],
        'cc'          : config['CC'],
        'bcc'         : config['BCC'],
        'report_name' : config['Report Name'],
        'table_title' : table_titles
    }

    header = {
        'API_KEY' : EMAILAPI_TOKEN
    }

    r = requests.request("POST", url = URL, headers=header, data = Data, files=uploadFiles)
    logger.debug(r)
    

#Step 1: Get list of devices from noco - for now local list
devicedata = noco_get_devices(CUSTOMER)

devicelist = []
for device in devicedata:
    if device['Snow Name']:
        #Step 2: get device data from snow - for now local list
        logger.debug(f"Fetching snow data for {device['Snow Name']}")
        snowdevice = query_Device(device['Snow Name'])
        #step 3: init device list with snow data
        if snowdevice:
            devicelist.append(classes.Device(device['Snow Name'], snowdevice, device['Type']))
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