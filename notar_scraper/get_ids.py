from fake_useragent import FakeUserAgent
from selectolax.parser import HTMLParser
from icecream import ic
import itertools
import asyncio
import logging
import chompjs
import hishel
import httpx
import json
import re
from urllib.parse import urlencode


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


def get_tasks(url: str, client: hishel.AsyncCacheClient):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Csrf-Token': '8a74b562665f7b36fada29d015244e929f5a61250e02bfd257547acdb4e90011',
        'Referer': 'https://www.notar.de/notarsuche/notarsuche',
        'Cookie': 'PHPSESSID=ogosglcfmdjcr2ape8ics8ch9a; persistence=!Y5TkfleOajjAUg/JUc6UGqEYcSRk6eM1oPv0o1vwjAda4HHSJ/uLtMnul1vcprgC3ZV/RUxWKe+a/yA='
    }
    tasks = []
    for idx in range(30):
        params = {
            'eID': 'bnotk_nvz',
            'filter[0]': 'excludeNonNotaryChambers:true',
            'filter[1]': 'excludeBadenWurttembergSpecificOfficialTitles:true',
            'filter[2]': 'hideDisabled:true',
            'filter[3]': 'activeOnly:true',
            'filter[4]': 'excludeFutureNotaries:true',
            'filter[5]': f'chamberId:{idx}',
            'sort': 'lastName,asc',
            'endpoint': 'ext/notar.json',
            'start': '0'
        }
        request = client.get(url, headers=headers, params=params)
        tasks.append(request)
    return tasks


def parse(html_response: str) -> dict:
    parser = HTMLParser(html_response)
    ...
    return {}


def read_links(filename: str) -> list[str]:
    with open(f'{filename}.txt', 'r', encoding='utf-8') as file:
        return [link.replace('\n', '') for link in file.readlines()]


def save_jsonl(data: dict, filename: str = 'data') -> None:
    with open(f'{filename}.jsonl', 'a', encoding='utf-8') as file:
        file.write(json.dumps(data) + '\n')


def save_json(data: dict | list, filename: str = 'data') -> None:
    with open(f'{filename}.json', 'w', encoding='utf-8') as file:
        file.write(json.dumps(data))


def save_csv(data: list[str], filename: str = 'data') -> None:
    with open(f'{filename}.csv', 'a', encoding='utf-8') as file:
        file.write(','.join(data))


def save_txt(data: list[str], filename: str = 'data') -> None:
    with open(f'{filename}.txt', 'a', encoding='utf-8') as file:
        [file.write(f'{line}\n') for line in data]


async def main():
    async with hishel.AsyncCacheClient(timeout=90) as client:
        url = 'https://www.notar.de/'
        tasks = get_tasks(url=url, client=client)
        batches = itertools.batched(tasks, 1)
        for batch in batches:
            responses: list[httpx.Response] = await asyncio.gather(*batch)
            for res in responses:
                data: dict = res.json()
                items: list[dict] = data.get('items')
                ids = [item.get('id') for item in items]
                save_txt(ids)


if __name__ == "__main__":

    asyncio.run(main=main())
