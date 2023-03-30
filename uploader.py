from utils import Utils
import json

utils = Utils()
with open('scraped-data.json', 'r') as f:
    _data = json.load(f)

data_copy = _data.copy()

for item in data_copy:
    try:
        utils.post(f'{item}--automatic')
    except Exception as e:
        # log the error, or take some other action
        print(f'Error occurred while processing {item}: {e}')
    _data.remove(item)

with open('scraped-data.json', 'w') as f:
    json.dump(_data, f, indent=2)