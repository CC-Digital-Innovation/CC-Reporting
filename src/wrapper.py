import csv
import json
import os
from pathlib import PurePath

import dotenv
import pysnow
import requests
from loguru import logger
from requests.exceptions import HTTPError

from DeviceModules import DataDomain, Isilon, NetAPP, Pure, UCS, VMAX, vmWare, XtremIO
from DeviceModules.classes import Device, Report


# ====================== Environment / Global Variables =======================
dotenv.load_dotenv(override=True)

CMDB_PATH = os.getenv('CMDB_Path')
CUSTOMER = os.getenv("CUSTOMER_NAME")
DATABASE_HEADER = {
    "Content-Type" : "application/json",
    "pscp_sec_token" : os.getenv('DB_TOKEN')
}
DATABASE_REPORT_URL = os.getenv('DB_REPORT_URL')
DATABASE_URL = os.getenv('DB_URL')
SNOW_INSTANCE = os.getenv('Snow_Instance')
SNOW_USERNAME = os.getenv('Snow_User')
SNOW_PASSWORD = os.getenv('Snow_Password')
SNOW_CLIENT = pysnow.Client(instance=SNOW_INSTANCE, user=SNOW_USERNAME, password=SNOW_PASSWORD)


# ================================= Functions =================================
def get_devices(customer_name: str) -> dict:
    database_payload = json.dumps({
        "customer_name" : customer_name
    })
    database_response = requests.post(DATABASE_URL, data=database_payload, headers=DATABASE_HEADER)
    logger.debug(database_response.content)
    
    if database_response.status_code == 201:
        return database_response.json()["devices"]
    else:
        return {"Error" : "Error retrieving devices"}


def send_report_data(report_data, type, company=CUSTOMER):
    payload = {
        'company': company,
        'type': type,
        'metrics': report_data
    }
    r = requests.post(f"{DATABASE_REPORT_URL}", json = payload , headers=DATABASE_HEADER)
    try:
        r.raise_for_status()
    except HTTPError as e:
        # send alert to custom HTTP endpoint
        logger.error(str(e))
        return str(e)
    return r.text


def query_Device(DeviceName):
    #Query client for Device by name
    table = SNOW_CLIENT.resource(api_path=CMDB_PATH)
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


# ================================ Main Method ================================
if __name__ == '__main__':
    logger.add("logs/{time:YYYY-MM-DD}_cc_reporting.log", rotation="00:00")
    
    logger.info("******************************")
    logger.info("******** Report Start ********")
    logger.info("******************************")
    
    # Step 1: Get list of devices from a database (Power Apps Dataverse) - for now local list
    devicedata = get_devices(CUSTOMER)
    devicelist = []
    for device in devicedata:
        if device['cr61f_devicename']:
            # Step 2: Get device data from ServiceNow - for now local list
            logger.debug(f"Fetching snow data for {device['cr61f_devicename']}")
            snowdevice = query_Device(device['cr61f_devicename'])
            
            # Step 3: Initialize device list with snow data
            if snowdevice:
                devicelist.append(Device(device['cr61f_devicename'], snowdevice, device['cr61f_devicetype@OData.Community.Display.V1.FormattedValue']))

    # Step 4: Iterate over list of devices
        #get data from device module
        #aggregate data

    module_map = {
            "DataDomain" : DataDomain,
            "Isilon"     : Isilon,
            #"Meraki"    : cisco_meraki,
            "Pure"       : Pure,
            "UCS"        : UCS,
            "VMAX"       : VMAX,
            "XtremIO"    : XtremIO,
            "NetApp"     : NetAPP,
            "vmWare"     : vmWare
    }

    reports = {
            "DataDomain" : Report(['Name', 'Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
            "Isilon"     : Report(['Name', 'Device', 'Alert Severity', 'Description']),
            "Meraki"     : Report(['Name', 'Device', 'Alert Severity', 'Description']),
            "Pure"       : Report(['Name', 'Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
            "UCS"        : Report(['Name', 'Device', 'Alert Severity', 'Description']),
            "VMAX"       : Report(['Name', 'Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
            "XtremIO"    : Report(['Name', 'Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
            #"NetApp"     : Report(),
            "vmWare"     : Report(['DatastoreName','Type','CapacityGB','FreeSpaceGB','UsedSpaceGB','PercentUsed','PercentFree','Accessible'])
    }

    for device in devicelist:
        if device.type in module_map.keys():
            logger.info(f"Starting report for {device.type}")
            try:
                reports[device.type] = module_map[device.type].get_report(device, reports[device.type])
            except Exception as e:
                logger.debug(e)

    # Step 5: Make report from aggregated data
    for device_type in reports.keys():
        report = reports[device_type]
        if hasattr(report, "dictData") and report.dictData:
            logger.info(f"Sending report for: {device_type}")
            send_report_data(report.dictData, device_type)
        if report.rows:
            report_csv = report.output_csv()
            with open(os.path.join('csvsdir', f"{CUSTOMER}_{device_type}_report.csv") , "w", newline='') as file:
                csvwrite = csv.writer(file)
                csvwrite.writerows(report.rows)
    
    # Step 6: Send data to Dataverse
    pass
