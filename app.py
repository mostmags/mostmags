from utils import Utils

# Initializing Variables
utils = Utils()
is_on = True

# Asking User to Enter Scrape Url
while is_on:
    url = input('Enter Url:')
    if url == 'stop':
        exit()
    elif url == 'clean':
        utils.clean_up()
    else:
        utils.post(url)