import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel
import ucsmsdk.mometa.fault.FaultInst as UCSFault
from ucsmsdk.ucshandle import UcsHandle


# Load environment variables.
load_dotenv()
UCS_IP_ADDRESS = os.getenv('UCS_IP_ADDRESS')
UCS_USERNAME = os.getenv('UCS_USERNAME')
UCS_PASSWORD = os.getenv('UCS_PASSWORD')


class Alert(BaseModel):
    """
    Represents an alert that exists on a machine.

    Members:
        description (str): The description of the alert.
        affected_device (str): The device with the alert.
        severity (str): The severity of the alert.
    """

    description: str
    affected_device: str
    severity: str


def get_ucs_faults() -> List[UCSFault.FaultInst]:
    """
    Retrieves all faults on a Cisco UCS. Returns a list of UCSFault objects.

    Returns:
        List[UCSFault.FaultInst]: A list of all faults on the UCS.
    """

    # Initialize a handle to establish communication with the UCS.
    handle = UcsHandle(UCS_IP_ADDRESS, UCS_USERNAME, UCS_PASSWORD)
    handle.login()

    # Get all alerts on the UCS.
    ucs_alerts = handle.query_classid("faultInst")

    # Log out of the UCS and return the list of alerts.
    handle.logout()
    return ucs_alerts


def cleanse_ucs_faults(ucs_faults: List[UCSFault.FaultInst]) -> List[Alert]:
    """
    Converts the provided list of UCSFault objects into a list of alert objects

    Args:
        ucs_faults (List[UCSFault.FaultInst]): A list of UCSFault objects to convert.

    Returns:
        List[Alert]: The converted list of alerts from UCSFault objects.
    """

    # Put all the faults into a list of alerts.
    all_alerts = list[Alert]()
    for fault in ucs_faults:
        # Extract information from the fault into the alert object and add it to the return list.
        curr_alert = Alert(description=f"{fault.descr} | Cause: {fault.cause} | Code: {fault.code}",
                           affected_device=fault.dn, severity=fault.severity)
        all_alerts.append(curr_alert)
    
    # Return the faults as a list of alerts.
    return all_alerts


def get_alerts() -> List[Alert]:
    """
    Get alerts from a Cisco UCS device.

    Returns:
        List[Alert]: The list of active alerts on a Cisco UCS device.
    """

    # Get the faults from the UCS.
    ucs_faults = get_ucs_faults()
    alerts = cleanse_ucs_faults(ucs_faults)

    # Return the faults as a list of alerts.
    return alerts


def main():
    # Example on getting alerts from a Cisco UCS device and printing
    # them to the console.
    all_ucs_alerts = get_alerts()

    # Print the list of alerts on the UCS.
    for alert in all_ucs_alerts:
        print(alert)


if __name__ == "__main__":
    main()
