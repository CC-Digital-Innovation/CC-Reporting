import os
import subprocess
import io
from loguru import logger
from src import storage_device

GB = ((1/1024)/1024)

# cliname is defined in symcli configuration files. sid is last three digits of serial number
def get_capacity(cliname, sid):
    #Runs symcli commands to retrieve data. NO IP, USER/PASS REQUIRED HERE
    logger.info('Initializing symcli settings and discovery')
    os.environ[f"SYMCLI_CONNECT"] = cliname
    subprocess.run(["symcfg", "discover"])
    symcli = subprocess.run(["symcfg", "-sid", f"{sid}", "list", "-pool", "-thin",  "-TB"], capture_output=True)
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
    return storage_device.StorageDevice(round(used, 3), round(total, 3), GB, round(free, 3))