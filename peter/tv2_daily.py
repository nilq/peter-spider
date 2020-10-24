import bs4 as bs
import requests
import datetime
import data_cse

import asyncio
from aiofile import AIOFile, Writer

DANISH_DATES = ['januar', 'februar', 'marts', 'april', 'maj', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'december']
initial_day = datetime.datetime(2020, 6, 1)
current_day = initial_day

def decode_danish(text):
    return text.replace('Ã¥', 'å').replace('Ã¦', 'æ').replace('Ã¸', 'ø')

async def go_deeper(url):
    r     = requests.get(url)
    soup  = bs.BeautifulSoup(r.text, features='lxml')

    for by in soup.select('strong.tc_byline__author__name'):
        if by.text == 'Ritzau':
            title = decode_danish(soup.select("h1.tc_heading--1")[0].text)
            print(f'[aiwa moment] Found Ritzau: {title}')

            year  = current_day.year
            month = current_day.month
            day   = current_day.day

            paraphrases = await data_cse.search_title(title, f'{day}.')

            print([x for x in paraphrases if x != ''])

            return

async def crawl_tv2():
    current_day = initial_day
    for i in range((datetime.datetime.now() - initial_day).days):
        current_day += datetime.timedelta(days=1)

        year  = current_day.year
        month = current_day.month
        day   = current_day.day

        url_of_the_day = f'https://nyheder.tv2.dk/{year}-{str(month).zfill(2)}-{str(day).zfill(2)}-dagens-nyheder-{day}-{DANISH_DATES[month - 1]}'

        r      = requests.get(url_of_the_day)
        soup   = bs.BeautifulSoup(r.text, features='lxml')
        table  = soup.select('div.tc_richcontent')

        async def handle_post(post):
            links  = [a['href'] for a in post.select('a[href]')]

            if len(links) > 0 and 'tv2.dk' in links[0] and not 'mailto:' in links[0]:
                await go_deeper(links[0])

        coros = [handle_post(post) for post in table]
        await asyncio.gather(*coros)

loop = asyncio.get_event_loop()
loop.run_until_complete(crawl_tv2())