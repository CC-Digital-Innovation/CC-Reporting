import os
from typing import List

from dotenv import load_dotenv
import meraki
from pydantic import BaseModel


# Load environment variables.
load_dotenv()
MERAKI_API_KEY = os.getenv('MERAKI_API_KEY')
MERAKI_ORG_ID = os.getenv('MERAKI_ORG_ID')

# Cisco Meraki global variables.
MERAKI_DASHBOARD = meraki.DashboardAPI(api_key=MERAKI_API_KEY,
                                       output_log=False,
                                       print_console=False,
                                       suppress_logging=True)


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


def list_meraki_network_ids(organization_id: str) -> List[str]:
    """
    Returns a list of Meraki network IDs for the provided Meraki organization ID.

    Args:
        organization_id (str): The ID of the Meraki organization.

    Returns:
        List[str]: A list of Meraki network IDs.
    """

    # Get a list of networks from the Meraki organization.
    network_ids = list()
    meraki_networks_response = MERAKI_DASHBOARD.organizations.getOrganizationNetworks(organization_id)
    for network in meraki_networks_response:
        # Extract the ID from this network and append it to the return list.
        network_ids.append(network['id'])
    
    # Return the list of network IDs for this Meraki organization.
    return network_ids


def get_meraki_organization_alerts(network_ids: List[str]) -> List[dict]:
    """
    Retrieves all alerts in a Meraki organization. Returns a list of raw alert dictionaries.

    Returns:
        List[dict]: A list of all raw alert dictionaries.
    """

    # Iterate over the list of provided network IDs for a Meraki organization.
    raw_meraki_alerts = list()
    for network_id in network_ids:
        # Iterate over all alerts in this Meraki network.
        network_alerts_response = MERAKI_DASHBOARD.networks.getNetworkHealthAlerts(network_id)
        for network_alert in network_alerts_response:
            # Add the raw alert dictionary to the return list.
            raw_meraki_alerts.append(network_alert)
    
    # Return the list of raw alert dictionaries.
    return raw_meraki_alerts


def cleanse_meraki_organization_alerts(meraki_organization_alerts: List[dict]) -> List[Alert]:
    """
    Converts the provided list of meraki organization alert dictionaries into a list of Alert objects.

    Args:
        meraki_alerts (List[dict]): A list of meraki organization alert dictionaries to convert.

    Returns:
        List[Alert]: The converted list of alerts from a meraki organization.
    """

    # Put all the alert dictionaries into a list of alert objects.
    all_alerts = list[Alert]()
    for org_alert_dict in meraki_organization_alerts:
        # Extract information from the dictionary into the alert object and add it to the return list.
        curr_alert = Alert(description=f"Category: {org_alert_dict['category']} | Type: {org_alert_dict['type']}",
                           affected_device=org_alert_dict['scope']['devices'][0]['name'],
                           severity='info' if org_alert_dict['severity'] is None else org_alert_dict['severity'])
        all_alerts.append(curr_alert)
    
    # Return the alerts as a list of alerts.
    return all_alerts


def get_alerts() -> List[Alert]:
    """
    Return a list of the current alerts from a Meraki organization.

    Returns:
        List[Alert]: The list of the current alerts from a Meraki organization.
    """
    
    # Get the alerts from the Meraki organization.
    network_ids = list_meraki_network_ids(MERAKI_ORG_ID)
    raw_organization_alerts = get_meraki_organization_alerts(network_ids)
    alerts = cleanse_meraki_organization_alerts(raw_organization_alerts)

    # Return the alerts in Meraki as a list of alerts.
    return alerts


def main():
    # Example on getting alerts from a Meraki organization and printing
    # them to the console.
    all_meraki_alerts = get_alerts()

    # Print the list of alerts in the Meraki organization.
    for alert in all_meraki_alerts:
        print(alert)


if __name__ == "__main__":
    main()
