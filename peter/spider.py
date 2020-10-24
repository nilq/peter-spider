import bs4 as bs
import requests
import sys
import json
from datetime import datetime as dt

def decode_danish(text):
    return text.replace('Ã¥', 'å').replace('Ã¦', 'æ').replace('Ã¸', 'ø')

def resume_on_dr(url):
    r      = requests.get(url)
    soup   = bs.BeautifulSoup(r.text, features='lxml')
    result = soup.findAll('p', { 'class': 'dre-article-title__summary'})

    if len(result) > 0:
        return result
    
    table  = soup.findAll('div', { 'class': 'dre-speech' })

    for (i, x) in enumerate(table):
        if r := x.find('p'):
            return r.text

    if i > 2:
        print('[DR-crawler] Rip.')
        sys.exit(0)


def resume_on_tv2(url):
    r      = requests.get(url)
    soup   = bs.BeautifulSoup(r.text, features='lxml')
    table  = soup.findAll('div', { 'class': 'tc_richcontent' })

    for (i, x) in enumerate(table):
        if r := x.find('p'):
            return r.text

        if i > 2:
            print('[BT-crawler] BREAKING: Noget frækt og kode-agtigt gik galt!?')
            sys.exit(0)

def resume_on_bt(url):
    r     = requests.get(url)
    soup  = bs.BeautifulSoup(r.text, features='lxml')
    table = soup.findAll('div', { 'class': 'article-content' })

    for (i, x) in enumerate(table):
        if r := x.find('p'):
            return r.text

        if i > 2:
            print('[BT-crawler] BREAKING: Noget frækt og kode-agtigt gik galt!?')
            sys.exit(0)

def resume_on_eb(url):
    r     = requests.get(url)
    soup  = bs.BeautifulSoup(r.text, features='lxml')
    table = soup.findAll('div', { 'class': 'article-bodytext' })

    for (i, x) in enumerate(table):
        if r := x.find('p'):
            return r.text
        
        if i > 2:
            print('[BT-crawler] BREAKING: Noget frækt og kode-agtigt gik galt!?')
            sys.exit(0)

def spider():
    tv2 = decode_danish(resume_on_tv2('https://nyheder.tv2.dk/samfund/2020-10-23-statsministeriet-indkalder-til-pressemode'))
    dr  = decode_danish(resume_on_dr('https://www.dr.dk/nyheder/seneste/mette-frederiksen-indkalder-til-corona-pressemoede-klokken-1830'))
    bt  = decode_danish(resume_on_bt('https://www.bt.dk/politik/statsministeriet-indkalder-til-pressemode-om-corona'))
    eb  = decode_danish(resume_on_eb('https://ekstrabladet.dk/nyheder/politik/statsministeriet-indkalder-til-pressemoede-fredag-klokken-18.30/8338692'))

    with open('data.luksus', 'w', newline='') as file:
        json.dump(
            { f'tatsministeriet-indkalder-til-pressemode-{dt.now()}': [ dr, tv2, bt, eb ] },
            file,
            indent=4
        )

if __name__ == '__main__':
    spider()