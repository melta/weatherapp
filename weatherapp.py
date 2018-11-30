#!/usr/bin/env python

""" Script for scraping data from weather sites.
"""

import sys
import html
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


def get_request_headers():
    """ Returns custom headers for url requests.
    """

    return {'User-Agent': FAKE_MOZILLA_AGENT}


def get_page_source(url):
    """ Gets page source by given url address.
    """

    request = Request(url, headers=get_request_headers())
    page_source = urlopen(request).read()
    return page_source.decode('utf-8')


def get_locations(locations_url):
    locations_page = get_page_source(locations_url)
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


def configurate():
    locations = get_locations(ACCU_BROWSE_LOCATIONS)
    while locations:
        for index, location in enumerate(locations):
            print(f'{index + 1}. {location[0]}')

        selected_index = int(input('Please select location: '))
        location = locations[selected_index - 1]
        locations = get_locations(location[1])

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

    location_config = configuration[CONFIG_LOCATION]
    name, url = location_config['name'], location_config['url']

    return name, url


def get_weather_info(page_content):
    city_page = BeautifulSoup(page_content, 'html.parser')
    current_day_section = city_page.find(
        'li', class_='night current first cl')

    weather_info = {}
    if current_day_section:
        current_day_url = current_day_section.find('a').attrs['href']
        if current_day_url:
            current_day_page = get_page_source(current_day_url)
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


def get_accu_weather_info():
    city_name, city_url = get_configuration()
    content = get_page_source(city_url)
    produce_output(city_name, get_weather_info(content))


def main(argv):
    """ Main entry point.
    """

    KNOWN_COMMANDS = {'accu': get_accu_weather_info,
                      'config': configurate}

    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='Service name', nargs=1)
    params = parser.parse_args(argv)

    if params.command:
        command = params.command[0]
        if command in KNOWN_COMMANDS:
            KNOWN_COMMANDS[command]()
        else:
            print("Unknown command provided!")
            sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
