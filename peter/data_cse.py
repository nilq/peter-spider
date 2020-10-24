import requests
import bs4 as bs
import asyncio
import spider
import re

SEARCH_ENGINE_ID  = ''
API_KEY = ''

page = 1
start = (page - 1) * 10 + 1

async def search_title(title, date):
    url = f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={title}&start={start}'
    data = requests.get(url).json()

    async def handle_item(item):
        title = item.get('title')

        print(f"TITLE: {title}\n")

        link  = item.get('link')

        return await do_the_harlem_shake(link, date)

    coros = [handle_item(item) for _, item in enumerate(data.get('items')[:3], start=1)]
    # Returns list of first paragraphs for sites
    return await asyncio.gather(*coros)

def generic_resume(url, el, selector, date):
    r      = requests.get(url)
    soup   = bs.BeautifulSoup(r.text, features='lxml')
    table = soup.findAll(el, { 'class': selector})

    for (i, x) in enumerate(table):
        if r := x.find('p'):
            return r.text

        if i > 2:
            print(f'[GIANT WARNING] Failed to find paragraph on: {url}')
            return ''

async def do_the_harlem_shake(url, date):
    starting_url = url.split('.dk')[0].replace('www.', '')

    resume = '<default>'

    if starting_url == 'https://dr':
        resume = generic_resume(url, 'div', 'dre-speech', date)

        if resume == '':
            resume = generic_resume(url, 'div', 'dre-article-body__paragraph', date)
    
    if starting_url in ['https://nyheder.tv2', 'https://tv2']:
        resume = generic_resume(url, 'div', 'tc_richcontent', date)
    
    if starting_url in ['https://jv', 'https://faa']: 
        resume = generic_resume(url, 'div', 'article__text', date)
    
    if starting_url == 'https://bt':
        resume = generic_resume(url, 'div', 'article-content', date)
    
    if starting_url == 'https://eb':
        resume = generic_resume(url, 'div', 'article-bodytext', date)

    if starting_url == 'https://berlingske':
        resume = generic_resume(url, 'div', 'article-body', date)

    if starting_url == 'https://jyllands-posten':
        resume = generic_resume(url, 'div', 'artView__text__content', date)

    if starting_url == 'https://politiken':
        resume = generic_resume(url, 'div', 'article__body', date)

    resume = spider.decode_danish(resume or '')

    if resume == '<default>':
        # print(f'Missing parser for: {url}')
        return ''

    return resume
