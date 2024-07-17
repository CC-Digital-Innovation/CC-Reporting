import configparser

import DeviceModules.DataDomain as data_domain_module
from storage_device import StorageDevice


CONFIG = configparser.ConfigParser()
CONFIG.read('example_customer_config.ini')


def get_data_domain_alerts():
    pass


def get_data_domain_capacities() -> list[StorageDevice]:
    # Instantiate return object.
    data_domain_capacities = list[StorageDevice]

    # Collect list of Data Domain devices for this customer.
    data_domains = CONFIG.sections()

    # Loop through all customer Data Domain devices.
    for data_domain in data_domains:
        # Get Data Domain's credentials / IP address.
        data_domain_username = CONFIG.get(data_domain, "username")
        data_domain_password = CONFIG.get(data_domain, "password")
        data_domain_ip_address = CONFIG.get(data_domain, "ip_address")

        # Get the Data Domain's capacity.
        data_domain_capacity = data_domain_module.get_capacity(
            {"username": data_domain_username, "password": data_domain_password},
            data_domain_ip_address
        )

        # Add this Data Domain device's capacity to the list.
        data_domain_capacities.append(data_domain_capacity)

    # Return all the Data Domain's capacity information.
    return data_domain_capacities
