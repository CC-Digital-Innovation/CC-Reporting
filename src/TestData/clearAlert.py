from openJson import jsonR
import pandas as pd
# Test file that takes in a json file and outputs information onto console
# jsonR stands for json reader
# This is a test file to play with data manipulation of pandas dataframes to remove unnecessary columns and extract relevant information

# Initialize variables for data extraction
filePath = 'src/testdata/'
dd_fileName = 'ddAllertsPayload.json'
pure_fileName = 'purealert.json'
unity_fileName = 'unityalert.json'

# Load json files into objects
dd_data = jsonR(filePath + dd_fileName).loadJson()
pure_data = jsonR(filePath + pure_fileName).loadJson()
unity_data = jsonR(filePath + unity_fileName).loadJson()

# Load json files into easily readable format
dd_dumps = jsonR(filePath + dd_fileName).dumpsJson()
pure_dumps = jsonR(filePath + pure_fileName).dumpsJson()
unity_dumps = jsonR(filePath + unity_fileName).dumpsJson()

# Test loaded objects
# print(dd_data, pure_data, unity_data, sep='\n\n')

# Normalize json files into dataframes
dd_df = pd.json_normalize(dd_data["alert_list"])
pure_df = pd.json_normalize(pure_data)
unity_df = pd.json_normalize(unity_data["entries"])

# Manipulate dataframes to remove unnecessary columns and extract relevant information
dd_df = dd_df.drop(columns=["alert_id", "event_id" , "description", "node_id", "link","snmp_notification_oid", "name", "alert_gen_epoch", "clear_epoch", "status", "severity", "msg", "clear_additional_info"])
pure_df = pure_df.drop(columns=["details", "opened", "expected", "code", "actual"])
unity_df = unity_df.drop(columns=["@base", "updated", "content.state", "content.description", "links", "content.timestamp", "content.component.resource"])
dd_df["action"] = dd_df["action"].str.replace("\n", "").str.split().str.join(" ")

# Code to extract capacity data from dd dataframe
# def extract_integer(s):
#     parts = s.split('=')
#     if parts[1] == type(int):
#         return parts[1]
#     else:
#         return parts[1]


# dd_df["additional_info"] = dd_df["additional_info"].apply(extract_integer)

#            object_id                             additional_info       class                                             action
#           category component_type current_severity              event component_name
#             content.severity content.component.id
# Print dataframes
dd_df.set_index("id", inplace=True)
dd_df.fillna(inplace=True, value="N/A")
# Test code to rename columns
# dd_df.rename(columns={"additional_info": "Storage Capacity", "object_id": "Object Identification", "class" : "Class", "action": "Action"}, inplace=True)
# Code to automatically rename columns without manually entering it
dd_df.columns = [col.replace('_', ' ').title() for col in dd_df.columns]
dd_df.rename_axis("DD Alerts", inplace=True)

pure_df.set_index("id", inplace=True)
# pure_df.rename(columns = {"category": "Category", "component_type" : "Component Type", "current_severity" : "Current Severity", "event": "Event", "component_name": "Component Name"}, inplace=True)
pure_df.columns = [col.replace('_', ' ').title() for col in pure_df.columns]
pure_df.rename_axis("Pure Alerts", inplace=True)

unity_df.set_index("content.id", inplace=True)
unity_df.fillna(inplace=True, value="N/A")
unity_df.columns = [col.replace('.', ' ').title() for col in unity_df.columns]
# unity_df.rename(columns = {"content.severity": "Severity", "content.component.id" : "Component ID"}, inplace=True)
unity_df.rename_axis("Unity Alerts", inplace=True)

print(dd_df, pure_df, unity_df, sep='\n\n')

