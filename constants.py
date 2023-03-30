import os
import base64

# Getting Enviorment Variables
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

CREDENTIALS = ':'.join([os.environ['WP_USER'], os.environ['WP_PASS']])
TOKEN = base64.b64encode(CREDENTIALS.encode())
AUTH_HEADER = {'Authorization': 'Basic ' + TOKEN.decode('utf-8')}
WP_ENDPOINT = os.environ['WP_ENDPOINT']
NET_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.7",
}
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
WATERMARK_TEXT = 'MostMags.Com'