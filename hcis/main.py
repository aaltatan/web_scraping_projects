from bs4 import BeautifulSoup
from icecream import ic
import requests
from fake_useragent import FakeUserAgent
import json

with open("index.html", "r", encoding="utf8") as file:
    html = file.read()

soup = BeautifulSoup(html, "lxml")

table_rows = soup.select(".table-responsive tbody tr")

for row in table_rows:
    tarkhees_id = row.select_one("td:nth-child(2)").text
    faculty_name = row.select_one("td:nth-child(3)").text
    activity = row.select_one("td:nth-child(4)").text
    area = row.select_one("td:nth-child(5)").text
    city = row.select_one("td:nth-child(6)").text
    phone = row.select_one("td:nth-child(7)").text
    location = row.select_one("td:nth-child(8) a")
    if location:
        location = location.attrs.get("href")

    row_data: dict[str, str] = {
        "tarkhees_id": tarkhees_id,
        "faculty_name": faculty_name,
        "activity": activity,
        "area": area,
        "city": city,
        "phone": phone,
        "location": location,
    }

    with open('data.jsonl', 'a', encoding='utf-8') as file:
        file.write(json.dumps(row_data) + '\n')
