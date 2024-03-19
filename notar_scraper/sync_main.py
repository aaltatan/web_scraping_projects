import httpx
import logging
from icecream import ic
import json
from fake_useragent import FakeUserAgent
import itertools
from selectolax.parser import HTMLParser

logging.basicConfig(
    filemode='a',
    filename='logger.log',
    format='[%(asctime)s] %(levelname)s | %(name)s => %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def read_links(filename: str) -> list[str]:
    with open(f'{filename}.txt', 'r', encoding='utf-8') as file:
        return [link.replace('\n', '') for link in file.readlines()]

def save_jsonl(data: dict, filename: str = 'data') -> None:
    with open(f'{filename}.jsonl', 'a', encoding='utf-8') as file:
        file.write(json.dumps(data) + '\n')


with httpx.Client(timeout=90) as client:
    url = 'https://www.notar.de/'
    ua = FakeUserAgent()
    headers = {
      'Accept': '*/*',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
      'Referer': 'https://www.notar.de/notarsuche/notarsuche',
    }

    cookies = {}

    batches = itertools.batched(read_links('data'), 10)
    for batch in batches:

        res = httpx.get('https://www.notar.de/notarsuche/notarsuche', timeout=90)
        parser = HTMLParser(res.text)

        token = (
            parser
            .css_first('meta[name="csrf-token"]')
            .attributes
            .get('content')
        )
        ic(token)
        headers['Csrf-Token'] = token

        set_cookie = res.headers.get('Set-Cookie')
        headers['Cookie'] = set_cookie

        for id in batch:
            
            params = {
                'eID':'bnotk_nvz',
                'endpoint':f'notar/{id}.json'
            }

            response = client.get(url=url, 
                                  headers=headers, 
                                  params=params,
                                  cookies=cookies)
            
            logger.info(response.status_code)

            data: dict = response.json()

            logger.info(data)

            save_jsonl(data=data, filename='new_data_2')
