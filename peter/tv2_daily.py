import bs4 as bs
import requests
import datetime
import data_cse
import json
import dateutil.parser

import asyncio
from aiofile import AIOFile, Writer

DANISH_DATES = ['januar', 'februar', 'marts', 'april', 'maj', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'december']
initial_day = datetime.datetime(2020, 6, 1)
current_day = initial_day

def decode_danish(text):
    return text.replace('Ã¥', 'å').replace('Ã¦', 'æ').replace('Ã¸', 'ø')

async def go_deeper_politiken(url):
    try:
        r = requests.get(url, timeout=10)
    except:
        return

    soup = bs.BeautifulSoup(r.text, features='lxml')

    year  = current_day.year
    month = current_day.month
    day   = current_day.day

    date = f'{day}. {DANISH_DATES[month - 1][:3]}. {year} '
    title = f'{decode_danish(soup.select("h1.article__title")[0].text)}'.strip().replace('\n', '').replace('       ', '')

    # The rest is history
    if year < 2015:
        title = date + title

    print(f'POLITIKEN: {title}')

    paraphrases = await data_cse.search_title(title, f'{day}.')

    return (f"{data_cse.generic_resume(url, 'div', 'article__body')}", [
        [x for x in paraphrases if x != '']
    ])

async def go_deeper(url):
    try:
        r = requests.get(url, timeout=10)
    except:
        return

    soup = bs.BeautifulSoup(r.text, features='lxml')

    not_by_ritzau_maybe = True

    title = None

    for by in soup.select('strong.tc_byline__author__name'):
        if by.text != 'Ritzau':
            title = decode_danish(soup.select("h1.tc_heading--1")[0].text)
            print(f'[aiwa moment] Found NOT Ritzau: {title} @ {url}')
        else:
            not_by_ritzau_maybe = False

    if not_by_ritzau_maybe and title:
        year  = current_day.year
        month = current_day.month
        day   = current_day.day

        paraphrases = await data_cse.search_title(title, f'{day}.')

        return (f"{data_cse.generic_resume(url, 'div', 'tc_richcontent')}", [
                [x for x in paraphrases if x != '']
            ])

def datetime_decoder_hook(emp):
    if 'current_date' in emp:
        emp['current_date'] = dateutil.parser.parse(emp['current_date'])
    
    return emp

def default_datetime(obj): #pylint: disable=E0202
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()

async def crawl_politiken():
    current_day = initial_day
    data = {}

    with open('data.luksus') as f:
        data = json.load(f, object_hook=datetime_decoder_hook)
    
    if 'current_date' in data:
        current_day = data['current_date']
        print(f'CURRENT DATE: {current_day}')

    initial = current_day

    for i in range((datetime.datetime.now() - initial).days):
        current_day += datetime.timedelta(days=1)

        year  = current_day.year
        month = current_day.month
        day   = current_day.day

        url_of_the_day = f'https://politiken.dk/arkiv/{year}-{month}-{day}'

        r      = requests.get(url_of_the_day)
        soup   = bs.BeautifulSoup(r.text, features='lxml')
        links  = soup.select('a.archive-article__link')

        async def handle_post(link):
            print(link['href'])
            return await go_deeper_politiken(link['href'])

        coros = [handle_post(link) for link in links]
        new_data = await asyncio.gather(*coros)

        if len([x for x in new_data if x != None]) > 0 and len(new_data) > 0:
            for d in new_data:
                if d != None and len(d[1]) != 0:
                    data[d[0]] = d[1]

        if i % 2 == 0:
            with open('data.luksus', 'w', newline='') as file:
                data['current_date'] = current_day
                json.dump(data, file, indent=4, default=default_datetime)

async def crawl_tv2():
    current_day = initial_day
    data = {}

    with open('data.luksus') as f:
        data = json.load(f, object_hook=datetime_decoder_hook)
    
    if 'current_date' in data:
        current_day = data['current_date']

    initial = current_day

    for i in range((datetime.datetime.now() - initial).days):
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
                return await go_deeper(links[0])

        coros = [handle_post(post) for post in table]
        new_data = await asyncio.gather(*coros)

        if len([x for x in new_data if x != None]) > 0 and len(new_data) > 0:
            for d in new_data:
                if d != None and len(d[1]) != 0:
                    data[d[0]] = d[1]

        if i % 2 == 0:
            with open('data.luksus', 'w', newline='') as file:
                data['current_date'] = current_day
                json.dump(data, file, indent=4, default=default_datetime)

    with open('data.luksus', 'w', newline='') as file:
        data['current_date'] = current_day
        json.dump(data, file, indent=4, default=default_datetime)

loop = asyncio.get_event_loop()
loop.run_until_complete(crawl_politiken())