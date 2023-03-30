import imp
import os
from constants import NET_HEADER
from utils import Utils

utils = Utils()

scrapers_dir = f"{os.path.dirname(os.path.realpath(__file__))}/scrapers/"
for entry in os.scandir(scrapers_dir):
    if not entry.name.endswith('.py'):
        continue

    scraper = entry.name
    mod = imp.load_source(scraper, f"{scrapers_dir}{scraper}")
    utils.store_db(mod.all_posts(NET_HEADER))
