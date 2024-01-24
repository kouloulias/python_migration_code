import requests
import json
import os
import pandas as pd
from pprint import pprint

headers = {"Accept": "application/json"}

#! To use the script add credentials
query = {
    "key": "",
    "token": "",
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
outputfile = "Default_Process_Board.json"


def get_comments():
    comments = [["card_id", "comment", "creator", "created_at"]]
    with open(outputfile, "r") as f:
        data = json.load(f)
        for d in data:
            url = f"https://api.trello.com/1/cards/{d['id']}/actions"
            response = requests.request("GET", url, headers=headers, params=query)
            json_data = response.json()
            if len(json_data) <= 0:
                continue
            for action in json_data:
                if action["type"] != "commentCard":
                    continue
                item_id = find_item_by_column(
                api_key = api_key,
                board_id = "",
                column_id = "",
                column_value = f"{d['id']}",
                )
                if item_id is not None:
                    create_update_to_item(api_key=api_key, item_id=item_id, content = str(action['data']['text'] +"\n\u2022Created At: " + action["date"].split("T")[0] + "\n\u2022Creator: " + action["memberCreator"]["fullName"]))

    return comments
comments = get_comments()