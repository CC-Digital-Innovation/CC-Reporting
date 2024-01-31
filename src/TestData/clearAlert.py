import pandas as pd
import tempfile
import json
from pretty_html_table import build_table
from datetime import datetime, timezone, timedelta
from copy import deepcopy
# File that outputs charts and tables to html
# Add any json here and take the data you want to display and the code will output a css and html file with the nice formatted data


# Initialize variables for data extraction of multiple file test
# file_path = "TestData/"
# dd_fileName = 'ddAllertsPayload.json'
# pure_fileName = 'purealert.json'
# unity_fileName = 'unityalert.json'
# unity_alertcopy = 'unityalert copy.json'
# purealertcopy = 'purealert copy.json'
# fileArray = [dd_fileName, pure_fileName, unity_fileName, purealertcopy, unity_alertcopy]
# number_of_files = len(fileArray)

# Initialize variables for data extraction of single file test
file_path = "TestData/"
dd_fileName = 'ddAllertsPayload.json'
pure_fileName = 'purealert.json'
unity_fileName = 'unityalert.json'
fileArray = [dd_fileName, pure_fileName, unity_fileName]
number_of_files = len(fileArray)

# Load json file into object
def get_json_data(file_name, file_path):
    try:
        with open(file_path + file_name, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return f"The file '{file_path}' could not be found."
    except Exception as e:
        return f"An error occurred: {e}"
    
def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    
    wrapper.calls = 0
    return wrapper
calledList = []
@count_calls
def get_write_html(content, prefix, num_rows, num_cols, longMessage, total_length, pixel_width):
    try:
        # print(get_write_html.calls)
        # dfArray = []
        # dfArray.append(prefix.split()[0])
        # print(dfArray[0])
        calledList.append(get_write_html.calls)
        # Automate border rounding by inserting css into html file for each table
        # print("prefix: ", prefix,"\n", "num-rows: ", num_rows,"\n", "num-cols: ", num_cols,"\n", "longMessage: ", longMessage)
        if num_rows == 1 and num_cols == 1 and longMessage == False:
            css_table_insert = f"""
                        div.{prefix.split()[0]} p:nth-child(3) table.dataframe:nth-child(1) tbody:nth-child(2) tr:nth-child({num_rows}) td:nth-child(1) {{
                            border-radius: 0 0 15px 15px;  
                        }}
                        div.{prefix.split()[0]} h1
                        {{
                            width: 450px;
                        }}
                        div.{prefix.split()[0]} h2 {{
                            width: 450px;
                        }}
                        /* === BREAKPOINT MARKER === */"""
            insert_content = css_table_insert
        elif num_rows >=1 and num_cols > 1 and longMessage == False:
            css_table_insert = f"""
                        div.{prefix.split()[0]} p:nth-child(3) table.dataframe:nth-child(1) tbody:nth-child(2) tr:nth-child({num_rows}) td:nth-child(1) {{
                            border-radius: 0 0 0 15px;
                        }}
                        div.{prefix.split()[0]} p:nth-child(3) table.dataframe:nth-child(1) tbody:nth-child(2) tr:nth-child({num_rows}) td:nth-child({num_cols+1}) {{
                            border-radius: 0 0 15px 0;  
                        }}
                        div.{prefix.split()[0]} h1
                        {{
                            width: 925px;
                        }}
                        div.{prefix.split()[0]} h2 {{
                            width: 925px;
                        }}
                        div.{prefix.split()[0]} table {{
                            width: 925px;
                        }}
                        /* === BREAKPOINT MARKER === */"""
            insert_content = css_table_insert
            
        elif num_rows >=1 and num_cols > 1 and longMessage == True:
            css_table_insert = f"""
                        div.{prefix.split()[0]} p:nth-child(3) table.dataframe:nth-child(1) tbody:nth-child(2) tr:nth-child({num_rows}) td:nth-child(1) {{
                            border-radius: 0 0 0 15px;
                        }}
                        div.{prefix.split()[0]} p:nth-child(3) table.dataframe:nth-child(1) tbody:nth-child(2) tr:nth-child({num_rows}) td:nth-child({num_cols+1}) {{
                            text-align: left !important;
                            border-radius: 0 0 15px 0;  
                        }}
                        div.{prefix.split()[0]} h1
                        {{
                            width: 925px;
                        }}
                        div.{prefix.split()[0]} h2 {{
                            width: 925px;
                        }}
                        div.{prefix.split()[0]} table {{
                            width: 925px;
                        }}
                        /* === BREAKPOINT MARKER === */"""
            insert_content = css_table_insert
        current_time_utc = datetime.now(timezone.utc)
        edt_offset = timedelta(hours=4)
        current_time_edt = current_time_utc - edt_offset
        formatted_date = current_time_edt.strftime('%Y-%m-%d | %H:%M:%S EDT')
        if len(calledList) == 1:
            with open('table_report.html', 'w') as file:
                file.write(f"""
                <html>
                    <head>
                        <style>
                            body {{
                                background-image: url("testdata/underwater.jpg");
                                background-repeat: no-repeat;
                                background-size: cover;
                                background-position: center center;
                                background-attachment: fixed;
                                
                            }}
                            p{{
                                margin: 0 auto;
                                /*width: 1250px;*/                 
                            }}
                    
                            h1, h2 {{
                                color: #ffffff; /* White text color for better contrast */
                                font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
                                font-size: 21px; /* Set the font size */
                                width: 450px;
                            }}
                            h1 {{
                                background-color: #305496; /* Dark blue background color */
                                border-top: 1px solid white; /* Dark blue border color */
                                border-left: 1px solid white; /* Dark blue border color */
                                border-right: 1px solid white; /* Dark blue border color */
                                font-size: 24px; /* Larger font size for h1 */
                                margin: 0 auto;
                                margin-top: 25px;
                                padding-top: 5px;
                                padding-bottom: 5px;
                                text-align: center;
                                border-radius: 15px 15px 0 0;
                                
                            }}
                            h2 {{
                                padding-top: 5px;
                                padding-bottom:5px;
                                background-color: #305496; /* Darker blue background color */
                                margin: 0 auto;
                                font-size: 20px; /* Slightly smaller font size for h2 */
                                border-left: 1px solid white; /* Dark blue border color */
                                border-right: 1px solid white; /* Dark blue border color */
                                text-align: center;
                            }}
                            table {{

                                margin: 0 auto;
                                border-radius: 0 0 15px 15px;
                                box-shadow: 0 4px 8px rgba(44, 62, 80, 0.2); /* Dark blue box shadow for table */
                                padding-top: 5px;
                                padding-bottom: 5px;
                                margin-bottom: 25px;
                                border-collapse: collapse;
                                width: 450px;
                                
                            }}
                            th, td{{
                                outline: 1px solid white; 
                                padding: 10px;
                            }}
                            div.cclogo{{
                                justify-content: center;
                                display: flex;
                                align-items: center;
                            }}
                            div.inner{{
                                text-align: center;
                                margin: 0 auto;  
                                size: fit-content;
                                height: 234px;
                                width: 414px;
                            }}
                            img.logo{{
                                height: 100%;
                                width: 100%;
                            }}
                            /* === BREAKPOINT MARKER === */
                            """)
                copyWidth = deepcopy(total_length)
            with open('table_report.html', 'r') as file:
                file_content = file.read()
            updated_content = file_content.replace("/* === BREAKPOINT MARKER === */", insert_content)
            with open('table_report.html', 'w') as file:
                file.write(updated_content)
                file.write("</style></head><body>")
                file.write(f"<div class='cclogo'><div class='inner'><img class='logo' src='testdata/cclogo.png'/></div></div><div class = '{prefix}'><h1>{prefix} Report</h1><h2>{formatted_date}</h2>" + content + "</div>")
        elif len(calledList) > 1 and len(calledList) < number_of_files:
            with open('table_report.html', 'r') as file:
                file_content = file.read()
            updated_content = file_content.replace("/* === BREAKPOINT MARKER === */", insert_content)
            with open('table_report.html', 'w') as file:
                file.write(updated_content)
                file.write(f"<div class = '{prefix}'><h1>{prefix}</h1><h2>{formatted_date}</h2>" + content + "</div>")
        elif len(calledList) == number_of_files:
            with open('table_report.html', 'r') as file:
                file_content = file.read()
            
            updated_content = file_content.replace("/* === BREAKPOINT MARKER === */", insert_content)
            with open('table_report.html', 'w') as file:
                file.write(updated_content)
                file.write(f"<div class = '{prefix}'><h1>{prefix}</h1><h2>{formatted_date}</h2>" + content + "</div></body></html>")
    except Exception as e:
        return f"An error occurred: {e}"

def get_full_html(temp_file, prefix, num_rows, num_cols, longMessage, total_length, pixel_width):
    try:
        # Open temp_file and write the html content
        with open(temp_file, 'r', encoding = 'utf-8') as f:
            content = f.read()
            return get_write_html(content, prefix, num_rows, num_cols, longMessage, total_length, pixel_width)
    except Exception as e:
        return f"An error occurred: {e}"


def get_temp_html(df, prefix, num_rows, num_cols, longMessage, column_widths, total_length, pixel_width):
    try:
        print("column_widths: ", column_widths, "\n", "total_length: ", total_length, "\n", "pixel_width: ", pixel_width)
        max_width = str(int(sum(column_widths))) + "px"
        print("max_width: ", max_width)
        px_column_widths = [str(int(width)) + "px" for width in column_widths]
        print("px_column_widths: ", px_column_widths)
        with tempfile.NamedTemporaryFile(suffix='.html', prefix = prefix, delete_on_close=False) as temp:
            print("prefix: ", prefix, "\n","total length: ", total_length, "\n", "pixel width: ", pixel_width, "\n", column_widths)
            if num_rows == 1 and num_cols == 1:
                temp.write(build_table(df, 'blue_dark',  index = False, font_size = "25px",width_dict=px_column_widths, padding = "15px", border_bottom_color="white", text_align="center").encode('utf-8'))
                temp.flush()
            elif num_rows >= 1 and num_cols > 1 and longMessage == False:
                temp.write(build_table(df, 'blue_dark',  index = False, font_size = "25px",width_dict=px_column_widths, padding = "15px", border_bottom_color="white", text_align="center").encode('utf-8'))
                temp.flush()
            elif num_rows >= 1 and num_cols > 1 and longMessage == True:
                temp.write(build_table(df, 'blue_dark',  index = False, font_size = "25px",width_dict=px_column_widths, padding = "15px", border_bottom_color="white", text_align="center").encode('utf-8'))
                temp.flush()
            return get_full_html(temp.name, prefix, num_rows, num_cols, longMessage, total_length, pixel_width)
    except Exception as e:
        return f"An error occurred: {e}" 
    

def get_temp_csv(df, prefix, num_rows, num_cols, lenOfMessage, column_widths, total_length, pixel_width):
    #create temporary csv file
    try:
        with tempfile.NamedTemporaryFile(suffix='.csv', prefix = prefix, delete_on_close=False) as temp:
            if num_rows == 1 and num_cols == 1:
                df.to_csv(temp.name, index=False, header=True)
                temp_df = pd.read_csv(temp.name)
                longMessage = False
            elif num_rows >= 1 and num_cols > 1 and lenOfMessage == None:
                df.to_csv(temp.name, index=True, header=True)
                temp_df = pd.read_csv(temp.name)
                longMessage = False
            elif num_rows >= 1 and num_cols > 1 and lenOfMessage >= 100:
                df.to_csv(temp.name, index=True, header=True)
                temp_df = pd.read_csv(temp.name)
                longMessage = True
            return get_temp_html(temp_df, prefix, num_rows, num_cols, longMessage, column_widths, total_length, pixel_width)

        
    except Exception as e:
        return f"An error occurred: {e}"


    
def get_dd_active_alerts(dd_data):
    try:
        dd_df = pd.json_normalize(dd_data["alert_list"])
        # Set this to the active alerts setting
        dd_df = dd_df[dd_df["status"] == "active"]
        lenOfMessage = None
        dd_df = dd_df.drop(columns=["alert_id", "action","clear_epoch", "description", "node_id", "link", "snmp_notification_oid", "name", "status", "additional_info", "clear_additional_info"])
        dd_df["msg"] = dd_df["msg"].str.replace("\n", "").str.split().str.join(" ")
        dd_df['alert_gen_epoch'] = pd.to_datetime(dd_df['alert_gen_epoch'], unit='s', utc = True)
        dd_df['alert_gen_epoch'] = dd_df['alert_gen_epoch'].dt.tz_convert('US/Eastern')
        dd_df['alert_gen_epoch'] = dd_df['alert_gen_epoch'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        dd_df.set_index("id", inplace=True, drop=True)
        dd_df.fillna(inplace=True, value="")
        dd_df.rename(columns= {'msg': 'Message', 'alert_gen_epoch': 'Post Time', 'object_id': "Object", 'alert_gen_epoch': 'Post Time'}, inplace=True)
        dd_df.columns = [col.replace('_', ' ').title() for col in dd_df.columns]
        dd_df.rename_axis(" ", inplace=True)
        dd_df = dd_df.reindex(columns=["Post Time", "Severity", "Class", "Object", "Message"])
        prefix = "Data Domain Capacity Alerts"
        pixel_width = len(prefix) * (21 * 0.8)
        if dd_df.empty == True:
            dd_df = dd_df.drop(columns=["Post Time", "Severity", "Class", "Object"])
            dd_df.loc[''] = 'No Active Alerts'
            max_lengths = [max(dd_df[col].astype(str).apply(len).max(), len(col)) for col in dd_df.columns]
            num_rows, num_cols = dd_df.shape

            total_length = sum(max_lengths)
            scaling_factor = sum(max_lengths) / 100  # Scaling factor based on 100% being the total_length
            column_widths = [length / scaling_factor for length in max_lengths]

            return get_temp_csv(dd_df,prefix, num_rows, num_cols, lenOfMessage, column_widths, total_length, pixel_width)
        else:
            num_rows, num_cols = dd_df.shape

            total_length = sum(max_lengths)
            scaling_factor = sum(max_lengths) / 100  # Scaling factor based on 100% being the total_length
            column_widths = [length / scaling_factor for length in max_lengths]

            return get_temp_csv(dd_df, prefix ,num_rows, num_cols, column_widths, total_length, pixel_width)
    except Exception as e:
        return f"An error occurred: {e}"


def get_pure_active_alerts(pure_data):
    try:
        pure_df = pd.json_normalize(pure_data)
        # Set this to the active alerts setting
        lenOfMessage = None
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
        pixel_width = len(prefix) * (21 * 0.8)
        num_rows, num_cols = pure_df.shape

        max_lengths = [max(pure_df[col].astype(str).apply(len).max(), len(col)) for col in pure_df.columns]
        total_length = sum(max_lengths)
        scaling_factor = sum(max_lengths) / 100  # Scaling factor based on 100% being the total_length
        column_widths = [length / scaling_factor for length in max_lengths]


        return get_temp_csv(pure_df, prefix, num_rows, num_cols, lenOfMessage,column_widths, total_length, pixel_width)
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
        unity_df.set_index("content.id", inplace=True, drop=True)
        unity_df.reset_index(drop=False, inplace=True)
        lenOfMessage = len(unity_df.at[0, "content.message"])
        unity_df.set_index("content.id", inplace=True, drop=True)
        unity_df.fillna(inplace=True, value="")
        unity_df.columns = [col.replace('.', ' ').title() for col in unity_df.columns]
        unity_df.rename_axis("Unity ID", inplace=True)
        unity_df.rename(columns = {"Content Timestamp": "Time", "Content Message": "Message"}, inplace=True)
        unity_df = unity_df.reindex(columns=["Time", "Message"])
        prefix = "Unity Capacity Alerts Report"
        pixel_width = len(prefix) * (21 * 0.8)
        num_rows, num_cols = unity_df.shape

        max_lengths = [max(unity_df[col].astype(str).apply(len).max(), len(col)) for col in unity_df.columns]
        total_length = sum(max_lengths)
        scaling_factor = sum(max_lengths) / 100  # Scaling factor based on 100% being the total_length
        column_widths = [length / scaling_factor for length in max_lengths]

        return get_temp_csv(unity_df, prefix, num_rows, num_cols, lenOfMessage, column_widths, total_length, pixel_width)
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
                # if number of files is greater than 3
                # pure_data_copy = get_json_data(file_name = purealertcopy, file_path= file_path)
                # pure_df_copy = get_pure_active_alerts(pure_data_copy)
                # unity_data_copy = get_json_data(file_name = unity_alertcopy, file_path= file_path)
                # unity_df_copy = get_unity_active_alerts(unity_data_copy)

    except Exception as e:
        print(f"An error occurred: {e}")

