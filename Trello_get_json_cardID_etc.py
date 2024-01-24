# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json
from pprint import pprint
import csv
import os


# url = "https://api.trello.com/1/boards/UI6pMFYD/cards"
#url = "https://api.trello.com/1/checklists/653f992ac0d577374af7ecbe"
# url = "https://api.trello.com/1/cards/4v3Zozhy"
# url = "https://api.trello.com/1/cards/63d0ac13eb6ebe7dcd548dfc/actions"
# url = "https://api.trello.com/1/boards/4v3Zozhy/customFields"
# url = "https://api.trello.com/1/boards/4v3Zozhy/3a78790ddf38ed9636465bfd430547f135d09ad494916641d0903a9805c1bbe2"
# url = "https://api.trello.com/1/boards/4v3Zozhy/labels"
# url = "https://api.trello.com/1/cards/{id}/customFieldItems"
# url = "https://api.trello.com/1/boards/frjMm3Fo/checklists"

# url = "https://api.trello.com/1/cards/{id}/attachments"

# url = "https://api.trello.com/1/cards/653f990478e39ba2b847cce7/checklists"
# url = "https://api.trello.com/1/members/{id}"
# url = "https://api.trello.com/1/boards/NIGc0iCQ/cards/6489e3b55d33333da93010c5"

url = "https://api.trello.com/1/cards/63f8120d95291610023c2b5b/desc"



headers = {
  "Accept": "application/json"
}


query = {
  'key': '',
  'token': ''
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   params=query
)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

output_file = "r22fr21f.json"
with open(output_file, 'w') as file:
    json.dump(response.json(), file, indent=4)

print("done")
