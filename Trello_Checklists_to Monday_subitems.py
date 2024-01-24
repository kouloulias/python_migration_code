import requests
import json
from pprint import pprint
import csv
import os
import pandas as pd


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
    print(query)

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
        return {"success": "true"}
    else:
        return ("Request failed with status code:", response.status_code)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
outputfile = 'Default_Process_Board.json'

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
            if len(json_data) <=0:
                continue
            if f"{d['id']}" == '63a5e6176bff3e0107e6c48b':
                for checklist in json_data:
                    items = checklist['checkItems']
                    for item in items:
                        new_response = requests.request(
                            "GET",
                            f"https://api.trello.com/1/members/{item['idMember']}",
                            headers=headers,
                            params=query
                        )
                        try:
                            member_data = new_response.json()
                            pprint(member_data)
                            username = member_data['fullName']
                        except:
                            username = ''

                        new_item = [item['name'], item['state'], item['due'], username]
                        checklists.append(new_item)
                        
                        item_id = find_item_by_column(
                        api_key = api_key,
                        board_id = "",
                        column_id = "",
                        column_value = f"{d['id']}",
                        )
                        item_name = item['name'].replace('"', ' ')
                        if item_id is not None:
                            print(item['name'])
                            columns = {}
                            if item['due'] is not None:
                                columns['due_date'] = item['due'].split('T')[0]
                            if username != "":
                                columns['checklist_members'] = username
                            if item['state']!= "":
                                columns['completed_'] = item['state']
                            create_subitem(
                            api_key = api_key,
                            parent_item_id = item_id,
                            item_name = item_name,
                            column_values = columns,
                            create_labels_if_missing = "true",
                            )
    return checklists
checklists = get_checklist_data()
