from bs4 import BeautifulSoup
from icecream import ic
import json

with open("./JD __ Listing _.html", "r", encoding="utf-8") as file:
    html = file.read()

soup = BeautifulSoup(html, "lxml")

items = soup.select(".mainSpan.clearfix")

for item in items:
    name = item.select_one(".CmpName-Col-Freelist h2 span").text
    category = item.select_one(".CmpName-Col-Freelist .catgory-cmp span").text
    phone = item.select_one(".Phone-Col-Freelist").text.strip()
    po_box = item.select_one(".PObox-Col-Freelist .Box-List-Lbl span").text

    row: dict[str, str] = {
        "name": name,
        "category": category,
        "phone": phone,
        "po_box": po_box,
    }

    with open("data.jsonl", "a", encoding="utf-8") as file:
        file.write(json.dumps(row) + ",\n")

    ic(row)
