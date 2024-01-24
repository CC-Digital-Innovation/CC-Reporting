from typedStorageAlerts import ddStorageAlert, ddDNSAlert, pureAlert,unitySuccessAlert, pureSoftwareAlert,unityPoolAlert, pureUpgradeAlert, unityFilesystemAlert, unityBackupAlert, unitySoftwareAlert, unityHardwareAlert, uniqueObject, nonUniqueObject
import copy
import json
import dd, pure, unity

# Example test of possible dataclass implementations of the objects in eachObject.py
# Data is validated in seperate files and then imported here to test functionality of the dataclasses and their methods
# Useful when wanting to test the dataclasses and their methods without having to run the entire program
# Objects can then be initialized here and then tested or called to other locations in the project
# Target data can be extracted here after initializing necessary dataclasses
# This is a test file used to play with different ways of handeling the data
objectArray = []
jsonArray = []
for each in dd.ddObject.alert_list:
    ddInterestData = {}
    ddInterestData["msg"] = each.msg
    ddInterestData["additional_info"] = each.additional_info
    ddInterestData["alert_id"] = each.alert_id
    # ddInterestData["object_id"] = each.object_id
    if each.object_id is not None:
        ddInterestData["object_id"] = each.object_id
        print(ddStorageAlert.from_dict(ddInterestData))
        objectArray.append(ddStorageAlert.from_dict(ddInterestData))
    else:
        print(ddDNSAlert.from_dict(ddInterestData))
        objectArray.append(ddDNSAlert.from_dict(ddInterestData))
if dd.ddObject.paging_info is not None:
    ddInterestData = {}
    ddInterestData["current_page"] = dd.ddObject.paging_info.current_page
for each in pure.pureObject:
    pureInterestData = {}
    pureInterestData["component_name"] = each.component_name
    pureInterestData["event"] = each.event
    pureInterestData["current_severity"] = each.current_severity
    # print(pureStorageAlert.from_dict(pureInterestData))
    # objectArray.append(pureStorageAlert.from_dict(pureInterestData))
    if each.component_name == "NJPure":
        print(pureAlert.from_dict(pureInterestData))
        objectArray.append(pureAlert.from_dict(pureInterestData))
    elif each.component_name == "upgrades":
        print(pureUpgradeAlert.from_dict(pureInterestData))
        objectArray.append(pureUpgradeAlert.from_dict(pureInterestData))
    elif each.component_name == "cte.ethe":
        print(pureSoftwareAlert.from_dict(pureInterestData))
        objectArray.append(pureSoftwareAlert.from_dict(pureInterestData))

for each in unity.unityObject.entries:
    unityInterestData = {}
    if each.content.component != None:
        unityInterestData["message"] = each.content.message
        unityInterestData["id"] = each.content.component.id
        print(unityPoolAlert.from_dict(unityInterestData))
        objectArray.append(unityFilesystemAlert.from_dict(unityInterestData))
    elif each.content.message == "Your contract has been refreshed successfully.":
        unityInterestData["message"] = each.content.message
        print(unitySuccessAlert.from_dict(unityInterestData))
        objectArray.append(unitySuccessAlert.from_dict(unityInterestData))
    elif each.content.message == "The used space of a file system backup_fs under the NAS Server BRXFILESUNITY in the system nju400mgmt is over 75% full.":
        unityInterestData["message"] = each.content.message
        print(unityFilesystemAlert.from_dict(unityInterestData))
        objectArray.append(unityBackupAlert.from_dict(unityInterestData))
    elif each.content.message == "Storage resource backup_fs is operating normally":
        unityInterestData["message"] = each.content.message
        print(unitySuccessAlert.from_dict(unityInterestData))
        objectArray.append(unityHardwareAlert.from_dict(unityInterestData))
    elif each.content.message == "A recommended system software (version 5.3.0.0.5.120) is now available for download. Version 5.3.0.0.5.120 is the latest release. Refer to the 5.3.0 Release Notes on dell.com/support for all new features and known issues addressed.":
        unityInterestData["message"] = each.content.message
        print(unitySoftwareAlert.from_dict(unityInterestData))
        objectArray.append(unitySoftwareAlert.from_dict(unityInterestData))

        
        

# Test print the objectArray
# print(objectArray)
storageList = []
for each in objectArray:
    if type(each) == pureAlert:
        storageList.append(pureAlert.to_dict(each))
        # print(each.component_name)
        # print(pureStorageAlert.to_dict(each))
    elif type(each) == pureUpgradeAlert:
        storageList.append(pureUpgradeAlert.to_dict(each))
        # print(each.component_name)
        # print(pureStorageAlert.to_dict(each))
    elif type(each) == pureSoftwareAlert:
        storageList.append(pureSoftwareAlert.to_dict(each))
        # print(each.component_name)
        # print(pureStorageAlert.to_dict(each))
    elif type(each) == unityPoolAlert:
        storageList.append(unityPoolAlert.to_dict(each))
        # print(each.message)
        # print(unityStorageAlert.to_dict(each))
    elif type(each) == unityBackupAlert:
        storageList.append(unityBackupAlert.to_dict(each))
        # print(each.message)
        # print(unityStorageAlert.to_dict(each))
    elif type(each) == unityHardwareAlert:
        storageList.append(unityHardwareAlert.to_dict(each))
        # print(each.message)
        # print(unityStorageAlert.to_dict(each))
    elif type(each) == unitySoftwareAlert:
        storageList.append(unitySoftwareAlert.to_dict(each))
        # print(each.message)
        # print(unityStorageAlert.to_dict(each))
    elif type(each) == unitySuccessAlert:
        storageList.append(unitySuccessAlert.to_dict(each))
        # print(each.message)
        # print(unitySuccessAlert.to_dict(each))
    elif type(each) == ddStorageAlert:
        storageList.append(ddStorageAlert.to_dict(each))
        # print(each.msg)
        # print(ddStorageAlert.to_dict(each))
    elif type(each) == ddDNSAlert:
        storageList.append(ddDNSAlert.to_dict(each))
        # print(each.msg)
        # print(ddDNSAlert.to_dict(each))
    

# print(json.dumps(storageList, indent=4, sort_keys=True))

# print(pureInterestData)
# print(unityInterestData)
unique_dict_reprs = set()

# Create a new list with unique dictionaries
unique_dicts = []
for d in copy.deepcopy(storageList):
    # Convert each dictionary to a frozenset and check if it's already in the set
    d.pop("alert_id", None)
    d.pop("content_id", None)
    dict_repr = frozenset(d.items())
    if dict_repr not in unique_dict_reprs:
        # Add the representation to the set and add the dictionary to the new list
        unique_dict_reprs.add(dict_repr)
        unique_dicts.append(d)
# Test uniqueness of dictionaries
# print("Original list of dictionaries:")
# print(json.dumps(storageList, indent=4, sort_keys=True))

# print("\nList of unique dictionaries:")
# print(json.dumps(unique_dicts, indent=4, sort_keys=True))
# print(objectArray, unique_dicts, jsonArray)

uniqueObject = uniqueObject(uniqueList=unique_dicts)
nonUniqueObject = nonUniqueObject(nonUniqueList=storageList)
# print(uniqueObject.to_dict())
print(json.dumps(uniqueObject.to_dict(), indent=4, sort_keys=True))
print(json.dumps(nonUniqueObject.to_dict(), indent=4, sort_keys=True))
# Make a dataclass out of each dictionary entry inside of the unique_dicts list
# class a specific 


# For each dictionary inside of the unique_dicts list, create a dataclass instance
# and add it to a new list

# This 
