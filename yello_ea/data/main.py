import pandas as pd
import json


with open('data.jsonl', 'r', encoding='utf-8') as file:
    data = (json.loads(line[:-1]) for line in file.readlines()) 


df = pd.DataFrame(data)
df = df.sort_values(['category'])


df.to_excel('data.xlsx')