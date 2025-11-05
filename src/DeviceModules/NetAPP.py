#!/usr/bin/env python3
"""
NetApp ONTAP Capacity Report Generator
Generates a CSV report of aggregate, volume, and LUN capacity from NetApp ONTAP systems
"""

import requests
import json
from loguru import logger
from DeviceModules import classes
import sys
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings if using self-signed certificates
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class NetAppONTAP:
    """NetApp ONTAP REST API client"""

    def __init__(self, host, username, password, verify_ssl=False):
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}/api"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _get(self, endpoint, params=None):
        """Make GET request to ONTAP REST API"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params, verify=self.verify_ssl)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.debug(f"Error making API request to {endpoint}: {e}")
            sys.exit(1)

    def get_aggregates(self):
        """Get aggregate capacity information"""
        logger.info("Fetching aggregate capacity data...")
        endpoint = "storage/aggregates"
        params = {
            'fields': 'name,space,state,node.name'
        }
        return self._get(endpoint, params)

    def get_volumes(self):
        """Get volume capacity information"""
        logger.info("Fetching volume capacity data...")
        endpoint = "storage/volumes"
        params = {
            'fields': 'name,size,space,state,aggregates.name,svm.name,type'
        }
        return self._get(endpoint, params)

    def get_luns(self):
        """Get LUN capacity information"""
        logger.info("Fetching LUN capacity data...")
        endpoint = "storage/luns"
        params = {
            'fields': 'name,space,location.volume.name,svm.name,enabled,os_type'
        }
        return self._get(endpoint, params)


def bytes_to_gb(bytes_value):
    """Convert bytes to GB with 2 decimal precision"""
    if bytes_value is None:
        return 0.0
    return round(bytes_value / (1024**3), 2)


def get_report(device: classes.Device, report: classes.Report):
    logger.info("Pulling data and creating report...")
   # Initialize NetApp ONTAP client
    netapp = NetAppONTAP(device.ip, device.username, device.password, False)

    # Collect capacity data
    aggregates = netapp.get_aggregates()
    volumes = netapp.get_volumes()
    luns = netapp.get_luns()


    # Aggregate section
    report.rows.append(['AGGREGATE CAPACITY REPORT'])
    report.rows.append(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    report.rows.append([])
    report.rows.append(['Aggregate Name', 'Node', 'State', 'Total (GB)', 'Used (GB)', 'Available (GB)', 'Used %'])

    for agg in aggregates.get('records', []):
        space = agg.get('space', {})
        block_storage = space.get('block_storage', {})

        total = bytes_to_gb(block_storage.get('size'))
        used = bytes_to_gb(block_storage.get('used'))
        available = bytes_to_gb(block_storage.get('available'))
        used_pct = round((used / total * 100) if total > 0 else 0, 2)

        report.rows.append([
            agg.get('name', 'N/A'),
            agg.get('node', {}).get('name', 'N/A'),
            agg.get('state', 'N/A'),
            total,
            used,
            available,
            used_pct
        ])

    # Volume section
    report.rows.append([])
    report.rows.append(['VOLUME CAPACITY REPORT'])
    report.rows.append([])
    report.rows.append(['Volume Name', 'SVM', 'Aggregate', 'Type', 'State', 'Total (GB)', 'Used (GB)', 'Available (GB)', 'Used %'])

    for vol in volumes.get('records', []):
        space = vol.get('space', {})

        total = bytes_to_gb(vol.get('size'))
        used = bytes_to_gb(space.get('used'))
        available = bytes_to_gb(space.get('available'))
        used_pct = round((used / total * 100) if total > 0 else 0, 2)

        # Get aggregate name (first one if multiple)
        agg_name = 'N/A'
        aggregates_list = vol.get('aggregates', [])
        if aggregates_list and len(aggregates_list) > 0:
            agg_name = aggregates_list[0].get('name', 'N/A')

        report.rows.append([
            vol.get('name', 'N/A'),
            vol.get('svm', {}).get('name', 'N/A'),
            agg_name,
            vol.get('type', 'N/A'),
            vol.get('state', 'N/A'),
            total,
            used,
            available,
            used_pct
        ])

    # LUN section
    report.rows.append([])
    report.rows.append(['LUN CAPACITY REPORT'])
    report.rows.append([])
    report.rows.append(['LUN Name', 'SVM', 'Volume', 'OS Type', 'Enabled', 'Size (GB)', 'Used (GB)', 'Used %'])

    for lun in luns.get('records', []):
        space = lun.get('space', {})

        size = bytes_to_gb(space.get('size'))
        used = bytes_to_gb(space.get('used'))
        used_pct = round((used / size * 100) if size > 0 else 0, 2)

        report.rows.append([
            lun.get('name', 'N/A'),
            lun.get('svm', {}).get('name', 'N/A'),
            lun.get('location', {}).get('volume', {}).get('name', 'N/A'),
            lun.get('os_type', 'N/A'),
            lun.get('enabled', 'N/A'),
            size,
            used,
            used_pct
        ])

    return report
