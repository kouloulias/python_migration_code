# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json
from pprint import pprint
import csv
import os


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


os.chdir(os.path.dirname(os.path.abspath(__file__)))
outputfile = 'Default_Process_Board.json'

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
        "Authorization": f'OAuth oauth_consumer_key="1ca8a2e1cc123bbf713628bc7641a5af", oauth_token="ATTAf1463a5ce829e4c2b455ee692d4265695a09e317863b7c7b550d96f37119c7c625BFFEDD"'
    }
    for file in files:
        response = requests.request(
            "GET",
            file[1],
            headers=headers_download
        )
        name = '.'.join(file[0].split('.')[:-1])
        file_name = f"{name}_{file[3].split('T')[0]}.{file[0].split('.')[-1]}"
        item_ids = find_item_by_column(
        api_key = api_key,
        board_id = "5439839810",
        column_id = "text8",
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
download_files(files)  
