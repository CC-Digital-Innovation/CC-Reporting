import requests
import urllib3
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import dotenv
import os
import json
import atexit
import ssl
import pandas as pd
import os

# Determine what the criteria for an alarm to go off should be
# These integers represent the percentage of memory, cpu, or storage capacity
# This integer acts as a threshold for the alarm to go off
# Threshold set to 3% for testing purposes only, so I can see the alarm go off
cpu_threshold = 3
memory_threshold = 3
storage_threshold = 3



# Load local instance of NocoDB env variables
dotenv.load_dotenv()
nocodb_url = os.getenv("nocodb_url")
xc_auth = os.getenv("nocodb_xcauth")

# Start session a disable certifcate verification
session = requests.session()
session.verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get local NocoDB data from their REST API
def get_nocodb_data():
    headers = {
        'xc-token': xc_auth
    }
    response = requests.get(nocodb_url, headers=headers)
    if response.status_code != 200:
        return {"error": "Error getting NocoDB data"}
    else:
        return response.text

# Parse the local NocoDB data
def get_parsed_nocodb_data(data):
    try:
        data = json.loads(data)
        envvariable_names = []
        envvariable_values = []
        for i in data["list"]:
            if i["enviornment variables"] != None:
                envvariable_names.append(i["enviornment variables"])
            if i["values"] != None:
                envvariable_values.append(i["values"])
        return envvariable_names, envvariable_values
    except:
        return {"error": "Error parsing NocoDB data"}

# Structure the enviornment variables from the local nocodb table into a dictionary
def get_allenv_variables():
    env_names, env_values = get_parsed_nocodb_data(get_nocodb_data())
    # Make a dictionary of each env_name to env_value
    env_dict = {}
    for i in range(len(env_names)):
        env_dict[env_names[i]] = env_values[i]
    return env_dict

# Load NocDB env variables
config = get_allenv_variables()

# Load vCenter env variables
vcenter_apihost = config["vcenter_apihost"]
vcenter_username = config["vcenter_username"]
vcenter_password = config["vcenter_password"]
vcenter_esxihost = config["vcenter_esxihost"]



# Create ssl context
context = None
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

# Connect to the vCenter server
si = SmartConnect(host=vcenter_apihost, 
                  user=vcenter_username, 
                  pwd=vcenter_password, 
                  sslContext=context)



def get_alarms(service_instance):
    content = service_instance.RetrieveContent()
    lis_of_alarms = []
    for ta in content.rootFolder.triggeredAlarmState:
        if ta.overallStatus == 'green':
            severity = 'Info'
        elif ta.overallStatus == 'yellow':
            severity = 'Warning'
        elif ta.overallStatus == 'red':
            severity = 'CRITICAL'
        alarm_dict = {
            'alarm_name': ta.alarm.info.name,
            'entity_name': ta.entity.name,
            'alarm_key': ta.alarm.info.key,
            'alarm_description': ta.alarm.info.description,
            'object': ta.entity.name,
            'time': str(ta.time),
            'acknowledged': ta.acknowledged,
            'acknowledged_time': str(ta.acknowledgedTime),
            'acknowledged_by_user': ta.acknowledgedByUser,
            'severity': severity
        }
        lis_of_alarms.append(alarm_dict)
    return lis_of_alarms


def create_memory_alarm(service_instance, memory_threshold):
    content = service_instance.RetrieveContent()
    alarm_manager = content.alarmManager
    AlarmSpec = vim.alarm.AlarmSpec()
    AlarmSpec.dynamicType = None
    AlarmSpec.dynamicProperty = None
    AlarmSpec.enabled = True
    AlarmSpec.name = f"Custom Memory Usage Alarm (TEST, {memory_threshold})"
    AlarmSpec.description = f"This is a custom memory alarm that goes off when memory exceeds {memory_threshold}% of capacity, please add more memory to this host"
    # Create a new MetricAlarmExpression
    metric_alarm_expression = vim.alarm.MetricAlarmExpression(
        dynamicType=None,
        dynamicProperty=None,
        operator="isAbove",
        type=vim.HostSystem,
        metric=vim.PerformanceManager.MetricId(
            dynamicType=None,
            dynamicProperty=None,
            counterId=24, # Memory counterID
            instance="",
        ),
        yellow=None,
        yellowInterval=None,
        red=memory_threshold * 100,
        redInterval=0,
    )
    
    # Set the expression property of the AlarmSpec
    AlarmSpec.expression = metric_alarm_expression
    
    AlarmSpec.action = None
    AlarmSpec.actionFrequency = None
    AlarmSpec.setting = vim.alarm.AlarmSetting(
        dynamicType=None,
        dynamicProperty=None,
        toleranceRange=0,
        reportingFrequency=300,
    )
    alarm_manager.Create(content.rootFolder, AlarmSpec)


def create_cpu_alarm(service_instance, cpu_threshold):
    content = service_instance.RetrieveContent()
    alarm_manager = content.alarmManager
    AlarmSpec = vim.alarm.AlarmSpec()
    AlarmSpec.dynamicType = None
    AlarmSpec.dynamicProperty = None
    AlarmSpec.enabled = True
    AlarmSpec.name = f"Custon CPU Usage Alarm (TEST, {cpu_threshold})"
    AlarmSpec.description = f"This is a custom CPU alarm that goes off when CPU usage exceeds {cpu_threshold}% of capacity, please add more CPU's to this host"
    
    # Create a new MetricAlarmExpression for CPU usage
    metric_alarm_expression = vim.alarm.MetricAlarmExpression(
        dynamicType=None,
        dynamicProperty=None,
        operator="isAbove",
        type=vim.HostSystem,
        metric=vim.PerformanceManager.MetricId(
            dynamicType=None,
            dynamicProperty=None,
            counterId=2,  # CPU usage counter ID
            instance="",
        ),
        yellow=None,
        yellowInterval=None,
        red=cpu_threshold * 100,  # CPU usage threshold 
        redInterval=0,
    )
    
    # Set the expression property of the AlarmSpec
    AlarmSpec.expression = metric_alarm_expression
    
    AlarmSpec.action = None
    AlarmSpec.actionFrequency = None
    AlarmSpec.setting = vim.alarm.AlarmSetting(
        dynamicType=None,
        dynamicProperty=None,
        toleranceRange=0,
        reportingFrequency=300,
    )
    alarm_manager.Create(content.rootFolder, AlarmSpec)

def create_storage_alert(service_instance, storage_threshold):
    content = service_instance.RetrieveContent()
    alarm_manager = content.alarmManager
    AlarmSpec = vim.alarm.AlarmSpec()
    AlarmSpec.dynamicType = None
    AlarmSpec.dynamicProperty = None
    AlarmSpec.enabled = True
    AlarmSpec.name = f"Custom Datastore Usage Alarm (TEST,{storage_threshold})"
    AlarmSpec.description = f"This is a custom disk usage alarm that goes off when disk usage exceeds {storage_threshold}% of capacity, please add more storage to this host"
    
    # Create a new MetricAlarmExpression for disk usage
    metric_alarm_expression = vim.alarm.MetricAlarmExpression(
        dynamicType=None,
        dynamicProperty=None,
        operator="isAbove",
        type=vim.Datastore,
        metric=vim.PerformanceManager.MetricId(
            dynamicType=None,
            dynamicProperty=None,
            counterId=279,  # Disk usage counter ID
            instance="",
        ),
        yellow=None,
        yellowInterval=None,
        red=storage_threshold * 100,  # Disk usage threshold 
        redInterval=None,
    )
    
    # Set the expression property of the AlarmSpec
    AlarmSpec.expression = metric_alarm_expression
    
    AlarmSpec.action = None
    AlarmSpec.actionFrequency = None
    AlarmSpec.setting = vim.alarm.AlarmSetting(
        dynamicType=None,
        dynamicProperty=None,
        toleranceRange=0,
        reportingFrequency=300,
    )
    alarm_manager.Create(content.rootFolder, AlarmSpec)

def get_report(alert_object):
    # Factor payload into report style table
    # Load alert object
    # Create a table report
    active_alerts = []
    substring = "(TEST, 3)"
    for alert in alert_object:
        if alert["severity"] == "CRITICAL" or alert["severity"] == "Warning":
            if substring in alert["alarm_name"] or "(TEST,3)" in alert["alarm_name"]:
                alert_report = {}
                alert_report["Alarm Name"] = alert["alarm_name"]
                alert_report["Severity"] = alert["severity"]
                alert_report["Time"] = alert["time"]
                alert_report["Alarm Description"] = alert["alarm_description"]
                active_alerts.append(alert_report)
                
    return active_alerts


def get_df_json(report_data):
    try:
        df = pd.DataFrame(report_data)
        df["Time"] = pd.to_datetime(df["Time"])
        df['Time'] = df['Time'].dt.tz_convert('US/Pacific')
        df['Time'] = df['Time'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')

        df.to_json('vcenter_alerts.json', orient='records', indent=4)
        return df
    except Exception as e:
        print(e)






if __name__ == "__main__":
    # Get alarms gets all the active alarms from the vCenter server
    # print(json.dumps(get_alarms(si), indent=4, sort_keys=True))
    
    # Alarm definitions below(Threshold set at 3% For testing purposes only)
    # Descriptions can be changed to fit the need of the report and alarm

    # create_memory_alarm(si, memory_threshold)
    # create_cpu_alarm(si, cpu_threshold)
    # create_storage_alert(si, storage_threshold)

    print(get_df_json(get_report(get_alarms(si))))
    # print(get_temp_df_table(get_report(get_alarms(si))))
    # print(get_styled_table(get_temp_df_table(get_report(get_alarms(si)))))
    # print(json.dumps(get_report(get_alarms(si)), indent=4, sort_keys=True))
    atexit.register(Disconnect, si)
