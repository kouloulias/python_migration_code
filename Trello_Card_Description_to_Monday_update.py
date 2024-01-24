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


os.chdir(os.path.dirname(os.path.abspath(__file__)))
outputfile = 'Default_Process_Board.json'

with open(outputfile, 'r') as f:
  data = json.load(f)
# print(json.dumps(data, indent=4))

def get_files_data():
    files = []
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
                board_id = "",
                column_id = "",
                column_value = f"{d['id']}",
            )
            if item_id is not None:
              create_update_to_item(api_key=api_key, item_id=item_id, content=json_data['_value'])
    return files
files = get_files_data()
pprint(files)