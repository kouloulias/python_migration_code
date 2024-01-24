import requests
import json
from pprint import pprint
import csv
import os
import pandas as pd
import logging
import time


logging.basicConfig(filename = r'C:\Users\Kouloulias\Downloads\codes\logfile.txt', level= logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# boardsIDs = ['1', '2', '3', '4', '5', '6', '7', '8']
# mondayBoards = ['1', '2', '3', '4', '5', '6', '7', '8' ]

# boardsIds = {
#     'trello1': 'monday1',
#     'trello2': 'monday2',
#     'trello3': 'monday3',
#     'trello4': 'monday4',
#     'trello5': 'monday5',
#     'trello6': 'monday6',
#     'trello7': 'monday7',
#     'trello8': 'monday8'

# }
members = {'id1': 'Name1', 'id2': 'name2', 'id3': 'name3', 'id4': 'name4', 'id5': 'name5', 'id6': 'name6'}
allBoards = {
    'trelloX': 'mondayX',


}

headers = {
  "Accept": "application/json"
}


query = {
  'key': '',
  'token': ''
}

api_key = ""

def find_item_by_column(
    api_key: str, board_id: str, column_id: str, column_value: str
) -> str | None:
    url = "https://api.monday.com/v2"
    headers = {"Content-Type": "application/json", "Authorization": f"{api_key}"}

    query = {
        "query": "query { items_by_column_values (board_id: "
        + board_id
        + ', column_id: "'
        + column_id
        + '", column_value: "'
        + column_value
        + '") { id name } }'
    }

    response = requests.post(url, headers=headers, json=query)

    if response.status_code == 200:
        result = response.json()
        try:
            item_id = result["data"]["items_by_column_values"][0]["id"]
            return item_id
        except:
            return None
    else:
        return str(response.status_code)

def create_subitem(
    api_key: str,
    parent_item_id: str,
    item_name: str,
    column_values: dict = {},
    create_labels_if_missing: str = "true",
):
    url = "https://api.monday.com/v2"
    headers = {"Content-Type": "application/json", "Authorization": f"{api_key}"}

    def compose_column_values_string(columns: dict):
        if not columns:
            return r"{}"

        result = r"{"
        for key, val in column_values.items():
            result += r"\"" + key + r"\": " + r"\"" + val + r"\","
        result = result[:-1] + r"}"
        return result

    query = {
        "query": "mutation { create_subitem (parent_item_id:"
        + parent_item_id
        + ', item_name: "'
        + item_name
        + '", column_values: "'
        + compose_column_values_string(column_values)
        + '", create_labels_if_missing:'
        + create_labels_if_missing
        + ") { id board { id } }}"
    }
    # print(query)

    response = requests.post(url, headers=headers, json=query)
    if response.status_code == 200:
        result = response.json()
        return {
            "item_id": result["data"]["create_subitem"]["id"],
            "board_id": result["data"]["create_subitem"]["board"]["id"],
        }

    else:
        return ("Request failed with status code:", response.status_code)
    
def update_status(
    api_key: str, board_id: str, item_id: str, column_id: str, value: str
):
    url = "https://api.monday.com/v2"
    headers = {"Content-Type": "application/json", "Authorization": f"{api_key}"}
    mutation_query = {
        "query": "mutation { change_simple_column_value (item_id: "
        + item_id
        + ", board_id: "
        + board_id
        + ", column_id: "
        + column_id
        + ", value: "
        + value
        + ") { id } }",
    }
    response = requests.post(url, headers=headers, json=mutation_query)
    if response.status_code == 200:
        return response.json()
    else:
        return ("Request failed with status code:", response.status_code)


def add_file_to_column(
    api_key: str, item_id: str, column_id: str, file_name: str, file_content
):
    query = (
        "mutation ($file: File!) { add_file_to_column (file: $file, item_id: "
        + item_id
        + ', column_id: "'
        + column_id
        + '") { id } }'
    )

    url = "https://api.monday.com/v2/file"
    boundary = "xxxxxxxxxx"

    # Read the file content
    # with open(file_path, "rb") as file_content:
    # Construct the data for the multipart/form-data request
    data = f"--{boundary}\r\n"
    data += 'Content-Disposition: form-data; name="query"\r\n'
    data += "Content-Type: application/json\r\n\r\n"
    data += f"\r\n{query}\r\n"
    data += f"--{boundary}\r\n"
    data += f'Content-Disposition: form-data; name="variables[file]"; filename="{file_name}"\r\n'
    data += "Content-Type: application/octet-stream\r\n\r\n"

    # Encode the data as bytes
    payload = (
        data.encode("utf-8") + file_content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    )

    # Construct request headers
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": api_key,
    }

    # Make the request
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        result = response.json()
        print(result)
    else:
        print(f"Request failed with status code: {response.status_code}")

def create_update_to_item(api_key: str, item_id: str, content: str) -> dict:
    url = "https://api.monday.com/v2"
    headers = {"Content-Type": "application/json", "Authorization": f"{api_key}"}

    query = {
        "query": "mutation {create_update (item_id: "
        + item_id
        + ', body: "'
        + content
        + '") { id }}'
    }

    response = requests.post(url, headers=headers, json=query)

    if response.status_code == 200:
        return {"success": "true"}
    else:
        return {"Failed, status code": response.status_code}




for key, values in allBoards.items():
    board_url = f"https://api.trello.com/1/boards/{key}/cards"
    response = requests.request(
        "GET",
        board_url,
        headers=headers,
        params=query
    )
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    outputfile = f"{key}.json"
    with open(outputfile, 'w') as file:
        json.dump(response.json(), file, indent=4)

    #First Input Trello Comments
    def get_comments():
        comments = [["card_id", "comment", "creator", "created_at"]]
        with open(outputfile, "r") as f:
            data = json.load(f)
            for d in data:
                url = f"https://api.trello.com/1/cards/{d['id']}/actions"
                response = requests.request("GET", url, headers=headers, params=query)
                json_data = response.json()
                count = 0
                comment_count = sum(1 for action in json_data if action["type"] == "commentCard")
                print (comment_count)
                if len(json_data) <= 0:
                    continue
                for action in json_data:
                    if action["type"] != "commentCard":
                        continue
                    count = count + 1
                    item_id = find_item_by_column(
                    api_key = api_key,
                    board_id = f"{values}",
                    column_id = " ",
                    column_value = f"{d['id']}",
                    )
                    if item_id is not None:
                        create_update_to_item(api_key=api_key, item_id=item_id, content = str(action['data']['text'] +"\n\u2022Created At: " + action["date"].split("T")[0] + "\n\u2022Creator: " + action["memberCreator"]["fullName"]))
                        logging.info(d['id'] + " " +  f'{count}' + " / " + f"{comment_count}" + " Comments Migrated")
                if action["type"] == "commentCard":
                    logging.info(d['id'] + " " + " Comment Migration Completed")

        return comments
    comments = get_comments()



    #input Trello's Description

    def get_description_data():
        description = []
        with open(outputfile, 'r') as f:
            data = json.load(f)
            for d in data:
                url = f"https://api.trello.com/1/cards/{d['id']}/desc"
                response = requests.request(
                    "GET",
                    url,
                    headers=headers,
                    params=query
                )
                json_data = response.json()
                # print(json_data)
                if len(json_data['_value']) <=0:
                    continue
                item_id = find_item_by_column(
                    api_key = api_key,
                    board_id = f"{values}",
                    column_id = " ",
                    column_value = f"{d['id']}",
                )
                if item_id is not None:
                    create_update_to_item(api_key=api_key, item_id=item_id, content=json_data['_value'])
                    logging.info(d['id'] + " Description Migration Completed")
        return description
    description = get_description_data()

    #Download and input to monday Trello Attachments

    def get_files_data():
        files = []
        with open(outputfile, 'r') as f:
            data = json.load(f)
            for d in data:
                url = f"https://api.trello.com/1/cards/{d['id']}/attachments"
                response = requests.request(
                    "GET",
                    url,
                    headers=headers,
                    params=query
                )
                json_data = response.json()
                if len(json_data) <=0:
                    continue
                for file in json_data:
                    filed = [file['fileName'], file['url'],d['id'], file['date']]
                    files.append(filed)

        return files
    files = get_files_data()

    pprint(files)


    def download_files(files):
        # Replace 'YOUR_AUTHORIZATION_TOKEN' with your actual authorization token
        headers_download = {
            "Authorization": f'OAuth oauth_consumer_key=" ", oauth_token=" "'
        }
        count = 0
        for file in files:
            count = count + 1
            response = requests.request(
                "GET",
                file[1],
                headers=headers_download
            )
            name = '.'.join(file[0].split('.')[:-1])
            file_name = f"{name}_{file[3].split('T')[0]}.{file[0].split('.')[-1]}"
            item_ids = find_item_by_column(
            api_key = api_key,
            board_id = f"{values}",
            column_id = " ",
            column_value = file[2],
            )

            if item_ids is None:
                continue

            add_file_to_column(
            api_key = api_key,
            item_id = item_ids,
            column_id = "files",
            file_name = file_name,
            file_content = response.content,
            )                    
            logging.info(d['id']+ " " +f"{count}"+ " / "+f"{len(files)}" +" attachments have been downloaded")
            time.sleep(7)
    download_files(files)  


    #input Trello's Checklists
    def get_checklist_data():
        checklists = [['name', 'state', 'due','idMember']]
        with open(outputfile, 'r') as f:
            data = json.load(f)
            for d in data:
                url = f"https://api.trello.com/1/cards/{d['id']}/checklists"
                response = requests.request(
                    "GET",
                    url,
                    headers=headers,
                    params=query
                )
                json_data = response.json()
                count = 0

                if len(json_data) <=0:
                    continue
                for checklist in json_data:
                    count = count + 1
                    items = sorted(checklist['checkItems'], key=lambda x: x["pos"])
                    for item in items:
                        username = members.get(item['idMember'], "")
                        new_item = [item['name'], item['state'], item['due'], username]
                        checklists.append(new_item)
                        
                        item_id = find_item_by_column(
                        api_key = api_key,
                        board_id = f"{values}",
                        column_id = "text0",
                        column_value = f"{d['id']}",
                        )
                        item_name = item['name'].replace('"', ' ')

                        if item_id is not None:
                            print(item['name'])
                            columns = {}
                            if item['due'] is not None:
                                columns['date'] = item['due'].split('T')[0]
                            if username != "":
                                columns['text'] = username
                            if item['state']!= "":
                                columns['status'] = item['state']
                            if len(item_name) >250:
                                columns['long_text'] = item_name
                                create_subitem(
                                api_key = api_key,
                                parent_item_id = item_id,
                                item_name = item_name[:250],
                                column_values = columns,
                                create_labels_if_missing = "true",
                                )
                            else:
                                create_subitem(
                                api_key = api_key,
                                parent_item_id = item_id,
                                item_name = item_name,
                                column_values = columns,
                                create_labels_if_missing = "true",
                                )
                            logging.info(d['id'] + " " + f"{count}"+ " / " + f"{len(json_data)}" +" checklists have been created")

        return checklists
    checklists = get_checklist_data()
