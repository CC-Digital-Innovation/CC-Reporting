

object = {
    "uniqueList": [
        # dd Space Usage Alert
        {
            "additional_info": "SpaceUsage(%)=90",
            "msg": "Space usage in Data Collection has exceeded 90% threshold.",
            "object_id": "FilesysType=2"
        },
        # dd DNS Alert
        {
            "additional_info": "DNS-Servers = see output from net show dns",
            "msg": "Unable to communicate with configured DNS."
        },
        {
        # Pure Alert
            "component_name": "NJPure",
            "current_severity": "warning",
            "event": "EULA not accepted"
        },
        # Software Upgrade Alert
        {
            "component_name": "upgrades",
            "current_severity": "info",
            "event": "update completed"
        },
        # Hardware Success Alert
        {
            "component_name": "cte.ethe",
            "current_severity": "warning",
            "event": "failure"
        },
        {
        # Unity Storage Alert
            "id": "pool_2",
            "message": "Storage pool SAS Pool has exceeded its critical threshold of 95% (used+preallocated: 97%)."
        },
        {
        # Unity Backup Space Alert
            "id": "fs_58",
            "message": "The used space of a file system backup_fs under the NAS Server BRXFILESUNITY in the system nju400mgmt is over 75% full."
        },
        {
        # Unity Hardware Alert
            "id": "fs_58",
            "message": "Storage resource backup_fs is operating normally"
        },
        {
        # Unity Software Upgrade Alert
            "message": "A recommended system software (version 5.3.0.0.5.120) is now available for download. Version 5.3.0.0.5.120 is the latest release. Refer to the 5.3.0 Release Notes on dell.com/support for all new features and known issues addressed."
        },
        {
        # Unity Hardware Success Alert
            "message": "Your contract has been refreshed successfully."
        }
    ]
}