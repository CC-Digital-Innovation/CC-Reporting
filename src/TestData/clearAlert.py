import pandas as pd
import tempfile
import json
from pretty_html_table import build_table
from datetime import datetime, timezone, timedelta

# File that outputs charts and tables to html
# Add any json here and take the data you want to display and the code will output a css and html file with the nice formatted data


# Initialize variables for data extraction
file_path = "TestData/"
dd_fileName = 'ddAllertsPayload.json'
pure_fileName = 'purealert.json'
unity_fileName = 'unityalert.json'


# Load json file into object
def get_json_data(file_name, file_path):
    try:
        with open(file_path + file_name, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return f"The file '{file_path}' could not be found."
    except Exception as e:
        return f"An error occurred: {e}"
    

def get_write_html(content, prefix):
    try:
        current_time_utc = datetime.now(timezone.utc)
        edt_offset = timedelta(hours=4)
        current_time_edt = current_time_utc - edt_offset
        formatted_date = current_time_edt.strftime('%Y-%m-%d %H:%M:%S EDT')
        with open('table_report.html', 'a+') as file:                   
            if file.tell() == 0:
                file.write("""<html>
                <head>
                <style>
                    body {
                        background-image: url("testdata/waves.jpg");
                        background-repeat: no-repeat;
                        background-size: cover;
                        background-position: center center;
                        background-attachment: fixed;
                    }
                    p{
                        margin: 0 auto;
                        width: 1250px;                  
                    }
            
                    h1, h2 {
                        color: #ffffff; /* White text color for better contrast */
                        font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
                        font-size: 21px; /* Set the font size */
                    }
                    h1 {
                        background-color: #305496; /* Dark blue background color */
                        border-top: 1px solid white; /* Dark blue border color */
                        border-left: 1px solid white; /* Dark blue border color */
                        border-right: 1px solid white; /* Dark blue border color */
                        font-size: 24px; /* Larger font size for h1 */
                        width : 1250px;
                        margin: 0 auto;
                        margin-top: 25px;
                        padding-top: 5px;
                        padding-bottom: 5px;
                        text-align: center;
                        border-radius: 15px 15px 0 0;
                           
                    }
                    h2 {
                        padding-top: 5px;
                        padding-bottom:5px;
                        background-color: #305496; /* Darker blue background color */
                        width: 1250px;
                        margin: 0 auto;
                        font-size: 20px; /* Slightly smaller font size for h2 */
                        border-left: 1px solid white; /* Dark blue border color */
                        border-right: 1px solid white; /* Dark blue border color */
                        text-align: center;
                    }
                    table {
                        width: 1250px;
                        margin: 0 auto;
                        border-radius: 0 0 15px 15px;
                        box-shadow: 0 4px 8px rgba(44, 62, 80, 0.2); /* Dark blue box shadow for table */
                        padding-top: 5px;
                        padding-bottom: 5px;
                        margin-bottom: 25px;
                        border-collapse: collapse;
                           
                    }
                    th, td{
                        outline: 1px solid white; 
                        padding: 10px;
                    }
                    .Unity > p:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(3) {
                           text-align: left !important;
                    }
                    .Data > p:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(1) {
                        border-radius: 0 0 0 15px;
                    }
                    .Data > p:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(2) {
                        border-radius: 0 0 15px 0;
                    }
                    .Pure > p:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(1) {
                        border-radius: 0 0 0 15px;
                    }
                    .Pure > p:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(5) {
                        border-radius: 0 0 15px 0;
                    }
                    .Unity > p:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(1) {
                        border-radius: 0 0 0 15px;
                    }
                    .Unity > p:nth-child(3) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(3) {
                        border-radius: 0 0 15px 0;
                    }

                    div.cclogo{

                        font-size: 24px; /* Larger font size for h1 */
                        margin: 0 auto;
                        width: 1250px;
                        padding-top: 5px;
                        padding-bottom: 5px;
                        text-align: center;
                 }
                    img.logo{
                        width: 30%;
                        height: 30%;
                    }
                    
                </style>
                </head>
                """)
                # write the next line but with an image after the cclogo after h2 tag
                file.write(f"<div class='cclogo'><img class='logo' src='testdata/cclogo.png'/></div><div class = '{prefix}'><h1>{prefix} Report</h1><h2>Report Generated: {formatted_date}</h2>" + content + "</div>")
            else:
                file.write(f"<div class = '{prefix}'><h1>{prefix} Report</h1><h2>Report Generated: {formatted_date}</h2>" + content + "</div>")
    except Exception as e:
        return f"An error occurred: {e}"

def get_full_html(temp_file, prefix):
    try:
        # Open temp_file and write the html content
        with open(temp_file, 'r', encoding = 'utf-8') as f:
            content = f.read()
            return get_write_html(content, prefix)
    except Exception as e:
        return f"An error occurred: {e}"

def get_temp_html(df, prefix):
    try:
        with tempfile.NamedTemporaryFile(suffix='.html', prefix = prefix, delete_on_close=False) as temp:
            temp.write(build_table(df, 'blue_dark',  index = False, font_size = "25px",width = "300px", padding = "15px", border_bottom_color="white", text_align="center").encode('utf-8'))
            temp.flush()
            return get_full_html(temp.name, prefix)
    except Exception as e:
        return f"An error occurred: {e}" 

def get_temp_csv(df, prefix):
    #create temporary csv file
    try:
        with tempfile.NamedTemporaryFile(suffix='.csv', prefix = prefix, delete_on_close=False) as temp:
            df.to_csv(temp.name, index=True, header=True)
            temp_df = pd.read_csv(temp.name)
            return get_temp_html(temp_df, prefix)
    except Exception as e:
        return f"An error occurred: {e}"


    
def get_dd_active_alerts(dd_data):
    try:
        dd_df = pd.json_normalize(dd_data["alert_list"])
        # Set this to the active alerts setting
        dd_df = dd_df[dd_df["status"] == "active"]
        dd_df = dd_df.drop(columns=["alert_id", "action","clear_epoch", "description", "node_id", "link", "snmp_notification_oid", "name", "status", "additional_info", "clear_additional_info"])
        dd_df["msg"] = dd_df["msg"].str.replace("\n", "").str.split().str.join(" ")
        dd_df['alert_gen_epoch'] = pd.to_datetime(dd_df['alert_gen_epoch'], unit='s', utc = True)
        dd_df['alert_gen_epoch'] = dd_df['alert_gen_epoch'].dt.tz_convert('US/Eastern')
        dd_df['alert_gen_epoch'] = dd_df['alert_gen_epoch'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        dd_df.set_index("id", inplace=True)
        dd_df.fillna(inplace=True, value="")
        dd_df.rename(columns= {'msg': 'Message', 'alert_gen_epoch': 'Post Time', 'object_id': "Object", 'alert_gen_epoch': 'Post Time'}, inplace=True)
        dd_df.columns = [col.replace('_', ' ').title() for col in dd_df.columns]
        dd_df.rename_axis("DD ID", inplace=True)
        dd_df = dd_df.reindex(columns=["Post Time", "Severity", "Class", "Object", "Message"])
        prefix = "Data Domain Capacity Alerts"
        if dd_df.empty == True:
            dd_df = dd_df.drop(columns=["Post Time", "Severity", "Class", "Object"])
            dd_df.loc[''] = 'No Active Alerts'
            return get_temp_csv(dd_df,prefix)
        else:
            return get_temp_csv(dd_df, prefix)
    except Exception as e:
        return f"An error occurred: {e}"


def get_pure_active_alerts(pure_data):
    try:
        pure_df = pd.json_normalize(pure_data)
        # Set this to the active alerts setting
        pure_df = pure_df[pure_df["current_severity"] == "warning"]
        pure_df = pure_df.drop(columns=["details","category", "expected", "current_severity","code", "actual"])
        pure_df["opened"] = pd.to_datetime(pure_df["opened"], format='%Y-%m-%dT%H:%M:%SZ', utc=True)
        pure_df["opened"] = pure_df["opened"].dt.tz_convert('US/Eastern')
        pure_df["opened"] = pure_df["opened"].dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        pure_df.set_index("id", inplace=True)
        pure_df.columns = [col.replace('_', ' ').title() for col in pure_df.columns]
        pure_df.rename_axis("Pure ID", inplace=True)
        pure_df.rename(columns = {'Opened':'Date/Time (EDT)','Component Type': 'Component', 'Component Name': 'Name'}, inplace=True)
        pure_df = pure_df.reindex(columns=["Date/Time (EDT)", "Component", "Name", "Event"])
        prefix = "Pure Capacity Alerts Report"
        return get_temp_csv(pure_df, prefix)
    except Exception as e:
        return f"An error occurred: {e}"

def get_unity_active_alerts(unity_data):
    try:
        unity_df = pd.json_normalize(unity_data["entries"])
        # Set this to the active alerts setting
        unity_df = unity_df[unity_df["content.severity"] == 5]
        unity_df = unity_df.drop(columns=["@base", "updated", "content.state", "content.description", "links", "content.severity" ,"content.component.id", "content.component.resource"])
        unity_df["content.timestamp"] = pd.to_datetime(unity_df["content.timestamp"], format='%Y-%m-%dT%H:%M:%S.%fZ', utc=True)
        unity_df["content.timestamp"] = unity_df["content.timestamp"].dt.tz_convert('US/Eastern')
        unity_df["content.timestamp"] = unity_df["content.timestamp"].dt.strftime('%Y-%m-%d %H:%M %Z')
        unity_df.set_index("content.id", inplace=True)
        unity_df.fillna(inplace=True, value="")
        unity_df.columns = [col.replace('.', ' ').title() for col in unity_df.columns]
        unity_df.rename_axis("Unity ID", inplace=True)
        unity_df.rename(columns = {"Content Timestamp": "Time", "Content Message": "Message"}, inplace=True)
        unity_df = unity_df.reindex(columns=["Time", "Message"])
        prefix = "Unity Capacity Alerts Report"
        return get_temp_csv(unity_df,prefix)
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    # Get json data from file
    try:
        dd_data = get_json_data(file_name = dd_fileName, file_path= file_path)
        pure_data = get_json_data(file_name = pure_fileName, file_path= file_path)
        unity_data = get_json_data(file_name = unity_fileName, file_path= file_path)
        dd_df = get_dd_active_alerts(dd_data)
        pure_df = get_pure_active_alerts(pure_data)
        unity_df = get_unity_active_alerts(unity_data)
    except Exception as e:
        print(f"An error occurred: {e}")

