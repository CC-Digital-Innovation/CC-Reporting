import json

# Initialize variables for data extraction 
file_path = "TestData/"
dd_fileName = 'ddAllertsPayload copy.json'
pure_fileName = 'purealert.json'
unity_fileName = 'unityalert.json'
fileArray = [dd_fileName, pure_fileName, unity_fileName]
number_of_files = len(fileArray)

def get_json_data(file_name, file_path):
    try:
        with open(file_path + file_name, "r") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return f"The file '{file_path}' could not be found."
    except Exception as e:
        return f"An error occurred: {e}"
    
def get_dd_data():
    return get_json_data(dd_fileName, file_path)

def get_pure_data():
    return get_json_data(pure_fileName, file_path)

def get_unity_data():
    return get_json_data(unity_fileName, file_path)

def get_dd_td():
    # Get the data from the json file
    dd_payload = dict(get_dd_data())
    alert_list = list(dd_payload['alert_list'])
    paging_info = dict(dd_payload['paging_info'])
    page_links = list(paging_info['page_links'])

    target_dict = {}
    target_list = []

    # Loop through the alert_list and extract the data
    # I made a copy of the json file and then changed two status value to active to test this
    for alert in alert_list:
        if alert['status'] == 'active':
            target_dict['alert_id'] = alert['alert_id']
            target_dict['severity'] = alert['severity']
            target_dict['status'] = alert['status']
            target_dict['msg'] = alert['msg']
            target_list.append(target_dict.copy())
    return target_list

def get_pure_td():
    # Get the data from the json file
    pure_payload = list(get_pure_data())


    
    target_list = []
    target_dict = {}

    # Loop through the alert_list and extract the data
    # Find active alerts and extract them
    for alert in pure_payload:
        if alert['current_severity'] == 'warning':
            target_dict['id'] = alert['id']
            target_dict['current_severity'] = alert['current_severity']
            target_dict['component_name'] = alert['component_name']
            target_dict['component_type'] = alert['component_type']
            target_list.append(target_dict.copy())
    return target_list


def get_unity_td():
    # Get the data from the json file
    unity_payload = dict(get_unity_data())
    entries = list(unity_payload['entries'])


    target_list = []
    target_dict = {}


    # Loop through the entries and extract the data
    # Find the active alerts and extract them
    for entry in entries:
        if entry["content"]["severity"] == 5:
            target_dict['content_severity'] = entry["content"]["severity"]
            target_dict['content_id'] = entry["content"]["id"]
            target_dict['content_message'] = entry["content"]["message"]

            key_check = 'component'
            if key_check in entry["content"]:
                target_dict['content_component_id'] = entry["content"]["component"]["id"]

                
            target_list.append(target_dict.copy())
    return target_list

print(get_dd_td(), '\n', get_pure_td(), '\n', get_unity_td())