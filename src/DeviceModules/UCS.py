import os
from typing import List

from config import classes
import ucsmsdk.mometa.fault.FaultInst as UCSFault
from ucsmsdk.ucshandle import UcsHandle


def get_ucs_faults(device: classes.Device) -> List[UCSFault.FaultInst]:
    """
    Retrieves all faults on a Cisco UCS. Returns a list of UCSFault objects.

    Returns:
        List[UCSFault.FaultInst]: A list of all faults on the UCS.
    """

    # Initialize a handle to establish communication with the UCS.
    handle = UcsHandle(device.ip, device.username, device.password)
    handle.login()

    # Get all alerts on the UCS.
    ucs_alerts = handle.query_classid("faultInst")

    # Log out of the UCS and return the list of alerts.
    handle.logout()
    return ucs_alerts


def cleanse_ucs_faults(ucs_faults: List[UCSFault.FaultInst]) -> List[classes.Alert]:
    """
    Converts the provided list of UCSFault objects into a list of alert objects

    Args:
        ucs_faults (List[UCSFault.FaultInst]): A list of UCSFault objects to convert.

    Returns:
        List[Alert]: The converted list of alerts from UCSFault objects.
    """

    # Put all the faults into a list of alerts.
    all_alerts = list[classes.Alert]()
    for fault in ucs_faults:
        # Extract information from the fault into the alert object and add it to the return list.
        curr_alert = classes.Alert(description=f"{fault.descr} | Cause: {fault.cause} | Code: {fault.code}",
                           affected_device=fault.dn, severity=fault.severity)
        all_alerts.append(curr_alert)
    
    # Return the faults as a list of alerts.
    return all_alerts


def get_alerts(device: classes.Device) -> List[classes.Alert]:
    """
    Get alerts from a Cisco UCS device.

    Returns:
        List[Alert]: The list of active alerts on a Cisco UCS device.
    """

    # Get the faults from the UCS.
    ucs_faults = get_ucs_faults(device)
    alerts = cleanse_ucs_faults(ucs_faults)

    # Return the faults as a list of alerts.
    return alerts

def get_report(device: classes.Device, report: classes.Report):
    alerts = get_alerts(device)
    alertrows = []
    for alert in alerts:
        alertrows.append([alert.affected_device, alert.severity, alert.description])
    report.rows = alertrows
    return report