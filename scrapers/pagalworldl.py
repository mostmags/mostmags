import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import lxml

URL = 'https://pagalworldl.com'
def all_posts(header):
    _data = []
    soup = BeautifulSoup(requests.get(URL, headers=header).content, 'lxml')
    for post in soup.select('body > main > div:nth-child(9) > ul li'):
        _data.append(f'{URL}{post.find("a")["href"]}')
    return _data

def find_match(sentence, keyword_set):
    for word in sentence.split():
        if word in keyword_set:
            return word

def post_meta(url, header):
    soup = BeautifulSoup(requests.get(url, headers=header).content, 'lxml')
    data = {
        'type': 'post',
        'status': 'publish',
        "acf_fields": {
            "type": "Single",
        }
    }
    try:
        key_set = ['Mp3', 'Download']
        data['title'] = soup.select_one('title').text.split(find_match(soup.select_one('title').text, key_set))[0].strip()
        for tr in soup.select_one('.bpan table').select('tr'):
            for td in tr.select('td'):
                if td.text == 'Album' or td.text == 'Category' or td.text == 'Film':
                    data['acf_fields']['language'] = td.find_next_sibling('td').text.split('(', 1)[0].strip()
                elif td.text == '🎤 Singer(s)':
                    data['acf_fields']['singer'] = td.find_next_sibling('td').text.strip()
                elif td.text == '𝅘𝅥𝅯 Music Composer(s)':
                    data['acf_fields']['music_director'] = td.find_next_sibling('td').text.strip()
                elif td.text == '🖊 Lyric Writter(s)':
                    data['acf_fields']['lyricist'] = td.find_next_sibling('td').text.strip()
        
        data['acf_fields']['download_links'] = ''.join([urljoin(str(url), '/')[:-1], soup.select_one('a.dbutton')['href']]) 
        return data
    
    except AttributeError or KeyError:
        return None
