import requests
from bs4 import BeautifulSoup
import lxml
import re
from constants import NET_HEADER, WP_ENDPOINT, AUTH_HEADER, WATERMARK_TEXT
from PIL import Image, ImageDraw, ImageFont
import tldextract
from ytm import YouTubeMusic
import os
import json
from mutagen.mp3 import MP3
from importlib.machinery import SourceFileLoader
from slugify import slugify

class Utils:
    """
    This class contains various useful functions...
    """

    def __init__(self) -> None:
        self.error_happend = False

    def get_soup(self, url):
        return BeautifulSoup(requests.get(url, headers=NET_HEADER).content, 'lxml')

    def extract_flags(self, url):
        flags = re.findall("(--\w+)", url)
        if flags:
            url = re.sub("(--\w+)", "", url)
            return url, flags

        return url, []

    def callout_scraper(self, url):
        hostname = tldextract.extract(url).domain
        mod = SourceFileLoader(f"{hostname}", f"scrapers/{hostname}.py").load_module()
        return mod.post_meta(url, NET_HEADER)

    def download_file(self, url, filename):
        responce = requests.get(url, headers=NET_HEADER)
        with open(filename, 'wb') as f:
            f.write(responce.content)

        return True

    def change_mp3_meta(self, filename):
        file = MP3(filename)
        try:
            file.delete()
            file.save()
        except:
            print('Failed to remove mp3 metadata')

    def get_ytm_thumbnail(self, title, artist):
        api = YouTubeMusic()

        artist_query = artist.split(',')[0] if ',' in artist else artist
        search_query = f"{title} {artist_query}"
        
        for song in api.search_songs(search_query)['items'][:5]:
            if artist in str(song):
                return song['thumbnail']['url'].split('=')[0]
        
        return None

    def clean_up(self):
        currentFolder = os.getcwd()
        for item in os.listdir(currentFolder):
            if item.endswith('.mp3') or item.endswith('.jpg'):
                os.remove(os.path.join(currentFolder, item))

    def get_category(self, name):
        replacements = {'&': ',', 'Feat.': ',', 'Ft.': ','}
        for old, new in replacements.items():
            if old in name:
                name = name.replace(old, new)

        name = name.split(',')
        t_list = []

        for n in name:
            data = {
                'name': n
            }
            responce = requests.post(''.join([WP_ENDPOINT, 'categories']), headers=AUTH_HEADER, json=data).json()
            try:
                t_list.append(responce['data']['term_id'])
            except KeyError or IndexError:
                t_list.append(responce['id'])

        return t_list

    def check_media(self, name, type):
        response = requests.get(f'{WP_ENDPOINT}media?search={name}').json()
        for x in response:
            if f"{name}.{type}" in str(response):
                return x['id']
        return False
    
    def get_seo_title(self, data):
        if not '(' in data['title'] and not '-' in data['title']:
            if len(data['title']) < 26:
                if 'album' in data['acf_fields']:
                    return ' - '.join([data['title'], data['acf_fields']['album']])
                else:
                    return ' - '.join([data['title'], data['acf_fields']['singer']])
        
        return data['title']
    
    def media(self, url, filename, type):
        if self.download_file(url, filename):
            if type == 'img':
                self.resize_image(filename)
            else:
                self.change_mp3_meta(filename)
            
            checked_item = self.check_media(filename, type)
            if not checked_item:
                with open(filename, 'rb') as file:
                    response = requests.post(f"{WP_ENDPOINT}media", headers=AUTH_HEADER, files={'file': file}).json()
                return response['id']
            else:
                return checked_item['id']
            
    def resize_image(self, filename):
        im = Image.open(filename)
        im = im.resize((300, 300))
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype('ariblk.ttf', 15)
        textwidth, textheight = draw.textsize(WATERMARK_TEXT, font)
        width, height = im.size 
        x=width/2-textwidth/2
        y=height-textheight-270
        draw.text((x, y), WATERMARK_TEXT, font=font, stroke_width=2, stroke_fill='black') 
        im = im.save(filename)
        return filename

    def post_exists(self, query):
        
        response = requests.get(''.join([WP_ENDPOINT, 'posts?slug=', slugify(query)]))
        if response.status_code == 200:
            if len(response.json()) >= 1:
                return True
        
        return False

    def generate_excerpt(self, data):
        _excerpt = f'{data["title"]} Mp3 Song Download from '
        if "Tamil" in data["acf_fields"]["language"] or "Telugu" in data["acf_fields"]["language"]:
            _excerpt += 'Masstamilan'
        else:
            _excerpt += 'PagalWorld'
        
        _excerpt += f' Album in {data["acf_fields"]["language"]} music category, The Song Sung by {data["acf_fields"]["singer"]}, The Lyrics are written by {data["acf_fields"]["lyricist"]}, While The Music has composed by {data["acf_fields"]["music_director"]}. Download {data["title"]} mp3 song in 48Kbps, 192Kbps, and 320Kbps as High Quality Audio music.'
        return _excerpt

    def post(self, url):

        url, flags = self.extract_flags(url)

        data = self.callout_scraper(url)

        if '--customtitle' in flags:
            data['title'] = input('Enter your custom title:')
        
        automation = True if '--automatic' in flags else False
        forced = True if '--forced' in flags else False

        if not self.post_exists(f'{data["title"]}') or forced:

            data['excerpt'] = self.generate_excerpt(data)

            category = self.get_category(data['acf_fields']['language'])
            data['categories'] = category
            data['acf_fields']['language'] = category

            if ' - ' in data['title'] or '(' in data['title']:
                image_url = self.get_ytm_thumbnail(data['title'], '')
            else:
                image_url = self.get_ytm_thumbnail(data['title'], data['acf_fields']['singer'])

            if not image_url:
                if automation:
                    return False
                
                image_url = input('Enter Thumbnail Url:')

            data['featured_media'] = self.media(image_url, f'{data["title"]}-MostMags.jpg', 'img')
            mp3_id = self.media(data['acf_fields']['download_links'], f'{data["title"]}-MostMags.mp3', 'mp3')
            data['acf_fields']['download_links'] = [
                {
                    'song_file': {
                        'ID': mp3_id,
                        'id': mp3_id
                    }
                },
                {
                    'song_file': {
                        'ID': mp3_id,
                        'id': mp3_id
                    }
                },
                {
                    'song_file': {
                        'ID': mp3_id,
                        'id': mp3_id
                    }
                },
            ]
            response = requests.post(f'{WP_ENDPOINT}posts', headers=AUTH_HEADER, json=data)

            if response.status_code == 201:
                print(f'{data["title"]} is created...')
            else:
                print(f'{data["title"]} is failed to create...')
            self.clean_up()

        else:
            print('This post is already published...')
            return False

    def store_db(self, data):
        # Checking if file exists
        if os.path.exists('scraped-data.json'):

            # Getting scrape data 
            with open('scraped-data.json', 'r') as f:
                old_data = json.load(f)

            # Storing new data in old
            for link in data:
                if link not in old_data:
                    old_data.append(link)
            
            # Saving File
            with open('scraped-data.json', 'w') as f:
                json.dump(old_data, f, indent=2)

        else:
            with open('scraped-data.json', 'w') as f:
                json.dump(data, f, indent=2)