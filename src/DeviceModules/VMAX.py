import os
import subprocess
import io
from loguru import logger
from config import classes

GB = ((1/1024)/1024)

# cliname is defined in symcli configuration files. sid is last three digits of serial number
def get_capacity(name, symid):
    #Runs symcli commands to retrieve data. NO IP, USER/PASS REQUIRED HERE
    logger.info('Initializing symcli settings and discovery')
    os.environ[f"SYMCLI_CONNECT"] = name
    subprocess.run(["symcfg", "discover"])
    symcli = subprocess.run(["symcfg", "-sid", f"{symid}", "list", "-pool", "-thin",  "-TB"], capture_output=True)
    symcliout = symcli.stdout.decode()
    logger.debug(f'symcli error: {symcli.stderr}')

    #Searches output of symcli for the line that starts with TBs (has capacity totals)
    #Splits TBs line for required data
    #Sends data to helper function and adds dictionary to running list
    logger.info('Searching output for totals...')
    for line in io.StringIO(symcliout):
        split = line.split()
        if split:
            if split[0] == 'TBs':
                used  = float(split[3])*1024
                free  = float(split[2])*1024
                total = float(split[1])*1024
                return classes.StorageDevice(round(used, 3), round(total, 3), GB, round(free, 3))
    
    return classes.StorageDevice(0, 0, GB, 0)


def get_alerts(ip, usr, passw , head):
        #get active alerts
        alertslist = []
        alertsstr = ''
        for alert in alertslist:
                tempstring = f"{alert['severity']}: {alert['description']}\n"
                alertsstr = alertsstr + tempstring
                alertslist.append(tempstring)
        return {"alerts" : alertslist, "str" : alertsstr}


def get_report(device: classes.Device, report: classes.Report):
        headers = {
            'Content-Type': 'application/json'
        }
        caps = get_capacity(device.snowname, device.vmaxsid)
        #alerts = get_alerts(device.ip, device.username, device.password, headers)
        #alerts['str'], len(alerts['alerts'])
        row = [caps.used_storage, caps.total_storage, caps.free_storage]
        if report.rows:
                report.rows = report.rows.append(row)
        else:
            report.rows = [row]
        return report