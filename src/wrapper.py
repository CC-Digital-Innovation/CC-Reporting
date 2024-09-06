from DeviceModules import Isilon, DataDomain, Pure, UCS, VMAX, XtremIO
from config import classes
import tempfile
import os
import csv
import json
import pysnow
import configparser
import requests

#Set up globals
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join("config", "config.ini"))
URL = CONFIG.get('Email', 'url')
EMAILAPI_TOKEN = CONFIG.get('Email', 'Token')


def email_report(directory):
    uploadFiles = []
    table_titles = []
    for file in os.listdir(directory):
        print(file)
        table_titles.append(file.split(".")[0])
        uploadFiles.append(('files', open(os.path.join(directory, file), "rb")))

    Data = {
        'subject'     : CONFIG.get('Email', 'subject'),
        'to'          : CONFIG.get('Email', 'recipients'),
        'cc'          : CONFIG.get('Email', 'cc'),
        'bcc'         : CONFIG.get('Email', 'bcc'),
        'report_name' : CONFIG.get('Email', 'reportName'),
        'table_title' : table_titles
    }

    header = {
        'API_KEY' : EMAILAPI_TOKEN
    }

    r = requests.request("POST", url = URL, headers=header, data = Data, files=uploadFiles)
    print(r.json())
    


#Step 1: Get list of devices from noco - for now local list
#Step 2: get device data from snow - for now local list
with open(os.path.join("config", "devices.json"), "r") as devicefile:
    devicedata = json.load(devicefile)

#step 3: init device list with snow data
devicelist = []
for device in devicedata['devices']:
    devicelist.append(classes.Device(device['snowName'], device, device['type']))
#step 4: iterate over list of devices
    #get data from device module
    #aggregate data
module_map = {
        "DataDomain" : DataDomain,
        "Isilon"     : Isilon,
        #"Meraki"     : cisco_meraki,
        "Pure"       : Pure,
        "UCS"        : UCS
        #"VMAX"       : VMAX,
        #"XtremIO"    : XtremIO
    }
reports = {
        "DataDomain" : classes.Report(['Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
        "Isilon"     : classes.Report(['Device', 'Alert Severity', 'Description']),
        "Meraki"     : classes.Report(['Device', 'Alert Severity', 'Description']),
        "Pure"       : classes.Report(['Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
        "UCS"        : classes.Report(['Device', 'Alert Severity', 'Description'])
        #"VMAX"       : classes.Report(['Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count']),
        #"XtremIO"    : classes.Report(['Used space', 'Total Space', 'Free Space', 'alerts', 'alerts count'])
    }

for device in devicelist:
    if device.type in module_map.keys():
        curr_rows = reports[device.type].rows
        curr_rows.append(module_map[device.type].get_report(device))
        reports[device.type].rows = curr_rows

#step 5 make report from aggregated data
with tempfile.TemporaryDirectory() as csvdir:
    for key in reports.keys():
        temprep = reports[key]
        print(temprep.rows)
        if temprep.rows:
            with open(os.path.join(csvdir, f"{key}.csv") , "w") as file:
                csvwrite = csv.writer(file)
                csvwrite.writerow(temprep.headerRow)
                csvwrite.writerows(temprep.rows)
    #step 6 email report with email api
    email_report(csvdir)