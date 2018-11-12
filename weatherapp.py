#!/usr/bin/python3

""" Weather app project.
"""

import html
from urllib.request import urlopen, Request

ACCU_URL = "https://www.accuweather.com/uk/ua/lviv/324561/weather-forecast/324561"

# getting page from server
headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64;)'}
accu_request = Request(ACCU_URL, headers=headers)
accu_page = urlopen(accu_request).read()
accu_page = str(accu_page)

ACCU_TEMP_TAG = '<span class="large-temp">'
accu_temp_tag_size = len(ACCU_TEMP_TAG)
accu_temp_tag_index = accu_page.find(ACCU_TEMP_TAG)
accu_temp_value_start = accu_temp_tag_index + accu_temp_tag_size
accu_temp = ''
for char in accu_page[accu_temp_value_start:]:
    if char != '<':
        accu_temp += char
    else:
        break

print('AccuWeather: \n')
print(f'Temperature: {html.unescape(accu_temp)}\n')

