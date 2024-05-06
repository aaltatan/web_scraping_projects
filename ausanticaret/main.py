import requests
from fake_useragent import FakeUserAgent
import json

ua = FakeUserAgent()

endpoint = "https://ausanticaret.com/wp-json/wiloke/v2/listings"
params = {
    "postType": "factories",
    "postsPerPage": 12,
    "offset": 1,
    "pageNow": "search",
    "sc": "wil-async-grid",
}

whole_data: list = []

for i in range(1, 40):
    
    headers = {
        'User-Agent': ua.random
    }

    params["offset"] = i
    request = requests.get(url=endpoint, params=params, headers=headers)
    print(i, request.status_code)
    data: dict = request.json()
    data = data.get("listings")
    whole_data += data

with open("data.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(whole_data))
