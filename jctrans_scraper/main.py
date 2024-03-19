import json
import chompjs


with open('./log_final.log', 'r', encoding='utf-8') as file:
  for line in file.readlines():
    l = chompjs.parse_js_object(line[:-1])
    print(l)
    with open('data.jsonl', 'a', encoding='utf-8') as f:
      f.write(json.dumps(l) + '\n')


