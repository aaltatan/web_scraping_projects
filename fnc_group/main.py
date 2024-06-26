import requests
import chompjs
from rich import print
import json


res = requests.post(
  url='https://fnc-group.com/Sys/MemberDirectory/LoadMembers',
  data={
    'formId': '142414'
  },
  headers={'Accept': '*/*'}
)

data: str = res.text.replace('while(1); ', '')
json_data = json.loads(data)['JsonStructure']
data = chompjs.parse_js_object(json_data)


with open('data.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(data))