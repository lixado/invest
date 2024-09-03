# make a script that goes trought banks.json and fixes the icon urls by testing them using the following
import json
import requests
from urllib.parse import urljoin

possiblePaths = [
    '/favicon.ico',
    '/favicon.png',
    '/web/images/favicon.png',
    '/assets/favicon.ico',
    '/assets/images/favicon.ico',
]

def check_icon_url(base_url, path):
    url = urljoin(base_url, path)
    try:
        response = requests.head(url, timeout=5)
        return url if response.status_code == 200 else None
    except requests.RequestException:
        return None

def fix_icon_urls(data):
    for bank in data:
        if 'leverandorUrl' in bank:
            base_url = bank['leverandorUrl']
            for path in possiblePaths:
                valid_url = check_icon_url(base_url, path)
                if valid_url:
                    bank['icon_url'] = valid_url
                    break
            if 'icon_url' not in bank:
                bank['icon_url'] = ''  # Set empty string if no valid icon URL found

# Read the JSON file
with open('public/banks.json', 'r', encoding='utf-8') as file:
    banks_data = json.load(file)

# Fix icon URLs
fix_icon_urls(banks_data)

# Write the updated data back to the JSON file
with open('public/banks.json', 'w', encoding='utf-8') as file:
    json.dump(banks_data, file, ensure_ascii=False, indent=4)

print("Icon URLs have been updated in banks.json")
