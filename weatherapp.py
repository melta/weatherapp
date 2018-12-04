#!/usr/bin/env python

""" Script for scraping data from weather sites.
"""

import sys
import html
import time
import hashlib
import argparse
import configparser
from pathlib import Path
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

ACCU_URL = ("https://www.accuweather.com"
            "/uk/ua/lviv/324561/weather-forecast/324561")
ACCU_TAGS = ('<span class="large-temp">', '<span class="cond">')
ACCU_BROWSE_LOCATIONS = 'https://www.accuweather.com/uk/browse-locations'

FAKE_MOZILLA_AGENT = 'Mozilla/5.0 (X11; Fedora; Linux x86_64;)'

CONFIG_FILE = 'weatherapp.ini'
CONFIG_LOCATION = 'Location'

DEFAULT_LOCATION_NAME = 'Kyiv'
DEFAULT_LOCATION_URL = \
    'https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505'

CACHE_DIR = '.wappcache'
CACHE_TIME = 300


def get_request_headers():
    """ Returns custom headers for url requests.
    """

    return {'User-Agent': FAKE_MOZILLA_AGENT}


def get_cache_directory():
    return Path.home() / CACHE_DIR


def is_valid(path):
    """
    """
    return time.time() - path.stat().st_mtime < CACHE_TIME


def get_cache(url):
    """ Return cache by given url address if any.
    """

    cache = b''
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    cache_dir = get_cache_directory()
    if cache_dir.exists():
        cache_path = cache_dir / url_hash
        if cache_path.exists() and is_valid(cache_path):
            with cache_path.open('rb') as cache_file:
                cache = cache_file.read()
    return cache


def save_cache(url, page_source):
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    cache_dir = get_cache_directory()
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)

    with (cache_dir / url_hash).open('wb') as cache_file:
        cache_file.write(page_source)


def get_page_source(url, refresh=False):
    """ Gets page source by given url address.
    """

    cache = get_cache(url)
    if cache and not refresh:
        page_source = cache
        print(f'Cache for {url}')
    else:
        request = Request(url, headers=get_request_headers())
        page_source = urlopen(request).read()
        save_cache(url, page_source)
    return page_source.decode('utf-8')


def get_locations(locations_url, refresh=False):
    locations_page = get_page_source(locations_url, refresh=refresh)
    soup = BeautifulSoup(locations_page, 'html.parser')
    locations = []
    for location in soup.find_all('li', attrs={'class': 'drilldown cl'}):
        url = location.find('a').attrs['href']
        location = location.find('em').text
        locations.append((location, url))
    return locations


def get_configuration_file():
    """ Path to configuration file.

    Returns path to configuration file in your home directory.
    """

    return Path.home() / CONFIG_FILE


def save_configuration(name, url):
    """ Save selected location to configuration file.

    We don't want to configurate provider each time we use
    the application, thus we save preferred location in
    configuration file.

    :parma name: city name
    :param type: str

    :param url: Prefered location URL
    :param type: str
    """

    parser = configparser.ConfigParser()
    parser[CONFIG_LOCATION] = {'name': name, 'url': url}
    with open(get_configuration_file(), 'w') as configfile:
        parser.write(configfile)


def configurate(refresh=False):
    locations = get_locations(ACCU_BROWSE_LOCATIONS)
    while locations:
        for index, location in enumerate(locations):
            print(f'{index + 1}. {location[0]}')

        selected_index = int(input('Please select location: '))
        location = locations[selected_index - 1]
        locations = get_locations(location[1], refresh=refresh)

    save_configuration(*location)


def get_configuration():
    """ Returns configured location name and url.

    Raise `ProviderConfigurationError` error if configuration is
    broken or wasn't found.

    :return: city name and url
    :rtype: tuple
    """

    name = DEFAULT_LOCATION_NAME
    url = DEFAULT_LOCATION_URL
    configuration = configparser.ConfigParser()

    configuration.read(get_configuration_file())
    if CONFIG_LOCATION in configuration.sections():
        location_config = configuration[CONFIG_LOCATION]
        name, url = location_config['name'], location_config['url']

    return name, url


def get_weather_info(page_content, refresh=False):
    city_page = BeautifulSoup(page_content, 'html.parser')
    current_day_section = city_page.find(
        'li', class_='night current first cl')

    weather_info = {}
    if current_day_section:
        current_day_url = current_day_section.find('a').attrs['href']
        if current_day_url:
            current_day_page = get_page_source(current_day_url,
                                               refresh=refresh)
            if current_day_page:
                current_day = \
                    BeautifulSoup(current_day_page, 'html.parser')
                weather_details = \
                    current_day.find('div', attrs={'id': 'detail-now'})
                condition = weather_details.find('span', class_='cond')
                if condition:
                    weather_info['cond'] = condition.text
                temp = weather_details.find('span', class_='large-temp')
                if temp:
                    weather_info['temp'] = temp.text
                feal_temp = weather_details.find('span', class_='small-temp')
                if feal_temp:
                    weather_info['feal_temp'] = feal_temp.text

                wind_info = weather_details.find_all('li', class_='wind')
                if wind_info:
                    weather_info['wind'] = \
                        ' '.join(map(lambda t: t.text.strip(), wind_info))

    return weather_info


def produce_output(city_name, info):
    print('Accu Weather: \n')

    print(f'{city_name}')
    print("-"*20)
    for key, value in info.items():
        print(f'{key}: {html.unescape(value)}')


def get_accu_weather_info(refresh=False):
    city_name, city_url = get_configuration()
    content = get_page_source(city_url, refresh=refresh)
    produce_output(city_name, get_weather_info(content, refresh=refresh))


def main(argv):
    """ Main entry point.
    """

    KNOWN_COMMANDS = {'accu': get_accu_weather_info,
                      'config': configurate}

    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Service name', nargs=1)
    parser.add_argument('--refresh', help='Update caches', action='store_true')
    params = parser.parse_args(argv)

    if params.command:
        command = params.command[0]
        if command in KNOWN_COMMANDS:
            KNOWN_COMMANDS[command](refresh=params.refresh)
        else:
            print("Unknown command provided!")
            sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
