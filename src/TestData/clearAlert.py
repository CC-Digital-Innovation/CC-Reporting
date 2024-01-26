from openJson import jsonR
import pandas as pd
import tempfile
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

# Manipulate dataframes to remove unnecessary columns and extract relevant information, and standardize the time formatting
dd_df = dd_df.drop(columns=["alert_id", "action","clear_epoch", "description", "node_id", "link", "snmp_notification_oid", "name", "status", "additional_info", "clear_additional_info"])
dd_df["msg"] = dd_df["msg"].str.replace("\n", "").str.split().str.join(" ")
dd_df['alert_gen_epoch'] = pd.to_datetime(dd_df['alert_gen_epoch'], unit='s', utc = True)
dd_df['alert_gen_epoch'] = dd_df['alert_gen_epoch'].dt.tz_convert('US/Eastern')
dd_df['alert_gen_epoch'] = dd_df['alert_gen_epoch'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')

pure_df = pure_df.drop(columns=["details","category", "expected", "current_severity","code", "actual"])
pure_df["opened"] = pd.to_datetime(pure_df["opened"], format='%Y-%m-%dT%H:%M:%SZ', utc=True)
pure_df["opened"] = pure_df["opened"].dt.tz_convert('US/Eastern')
pure_df["opened"] = pure_df["opened"].dt.strftime('%Y-%m-%d %H:%M:%S %Z')

unity_df = unity_df.drop(columns=["@base", "updated", "content.state", "content.description", "links", "content.severity" ,"content.component.id", "content.component.resource"])
unity_df["content.timestamp"] = pd.to_datetime(unity_df["content.timestamp"], format='%Y-%m-%dT%H:%M:%S.%fZ', utc=True)
unity_df["content.timestamp"] = unity_df["content.timestamp"].dt.tz_convert('US/Eastern')
unity_df["content.timestamp"] = unity_df["content.timestamp"].dt.strftime('%Y-%m-%d %H:%M %Z')

# Print dataframes and obtain professional formatting
dd_df.set_index("id", inplace=True)
dd_df.fillna(inplace=True, value="")
dd_df.rename(columns= {'msg': 'Message', 'alert_gen_epoch': 'Post Time', 'object_id': "Object", 'alert_gen_epoch': 'Post Time'}, inplace=True)

dd_df.columns = [col.replace('_', ' ').title() for col in dd_df.columns]
dd_df.rename_axis("DD ID", inplace=True)
dd_df = dd_df.reindex(columns=["Post Time", "Severity", "Class", "Object", "Message"])

pure_df.set_index("id", inplace=True)
pure_df.columns = [col.replace('_', ' ').title() for col in pure_df.columns]
pure_df.rename_axis("Pure ID", inplace=True)
pure_df.rename(columns = {'Opened':'Date/Time (EDT)','Component Type': 'Component', 'Component Name': 'Name'}, inplace=True)
pure_df = pure_df.reindex(columns=["Date/Time (EDT)", "Component", "Name", "Event"])

unity_df.set_index("content.id", inplace=True)
unity_df.fillna(inplace=True, value="")
unity_df.columns = [col.replace('.', ' ').title() for col in unity_df.columns]
unity_df.rename_axis("Unity ID", inplace=True)
unity_df.rename(columns = {"Content Timestamp": "Time", "Content Message": "Message"}, inplace=True)
unity_df = unity_df.reindex(columns=["Time", "Message"])

def convert_epoch_to_datetime(df, column, output_column='datetime'):
    # Convert epoch times to datetime objects
    df[output_column] = pd.to_datetime(df[column], unit='s')

    return df


# Create temporary files for manipulated dataframes in csv format to be sent as emails in Email-API
with tempfile.NamedTemporaryFile(suffix='.csv', prefix = "ddCapacity", delete_on_close=False) as temp:
    dd_df.to_csv(temp.name)
    # print(temp.read())
    # print("\n\n")
    # print(temp.name)

with tempfile.NamedTemporaryFile(suffix='.csv', prefix = "pureCapacity", delete_on_close=False) as temp:
    pure_df.to_csv(temp.name)
    # print(temp.read())
    # print("\n\n")
    # print(temp.name)


with tempfile.NamedTemporaryFile(suffix='.csv', prefix = "unityCapacity", delete_on_close=False) as temp:
    unity_df.to_csv(temp.name)
    # print(temp.read())
    # print("\n\n")
    # print(temp.name)

print(dd_df, pure_df, unity_df, sep='\n\n')

