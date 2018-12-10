import re
import time
import hashlib
import configparser
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

import config


class AccuWeatherProvider:

    """ Weather provider for AccuWeather site.
    """

    def __init__(self):
        self.name = config.ACCU_PROVIDER_NAME

        location, url = self._get_configuration()
        self.location = location
        self.url = url

    def get_configuration_file(self):
        """ Path to configuration file.

        Returns path to configuration file in your home directory.
        """

        return Path.home() / config.CONFIG_FILE

    def _get_configuration(self):
        """ Returns configured location name and url.

        Raise `ProviderConfigurationError` error if configuration is
        broken or wasn't found.

        :return: city name and url
        :rtype: tuple
        """

        name = config.DEFAULT_LOCATION_NAME
        url = config.DEFAULT_LOCATION_URL
        configuration = configparser.ConfigParser()

        configuration.read(self.get_configuration_file())
        if config.CONFIG_LOCATION in configuration.sections():
            location_config = configuration[config.CONFIG_LOCATION]
            name, url = location_config['name'], location_config['url']

        return name, url

    def save_configuration(self, name, url):
        """ Save selected location to configuration file.

        We don't want to configure provider each time we use
        the application, thus we save preferred location in
        configuration file.

        :parma name: city name
        :param type: str

        :param url: Preferred location URL
        :param type: str
        """

        parser = configparser.ConfigParser()
        parser[config.CONFIG_LOCATION] = {'name': name, 'url': url}
        with open(self.get_configuration_file(), 'w') as configfile:
            parser.write(configfile)

    def get_request_headers(self):
        """ Return custom headers for url requests.
        """

        return {'User-Agent': config.FAKE_MOZILLA_AGENT}

    def get_url_hash(self, url):
        """ Generate url hash.
        """

        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def get_cache_directory(self):
        """ Return home directory for cache files.
        """

        return Path.home() / config.CACHE_DIR

    def is_valid(self, path):
        """ Check if cache is valid.

        Checks if cache file that corresponds to specified path
        is not obsolete.
        """

        return time.time() - path.stat().st_mtime < config.CACHE_TIME

    def get_cache(self, url):
        """ Return cache by given url address if any.
        """

        cache = b''
        cache_dir = self.get_cache_directory()
        if cache_dir.exists():
            cache_path = cache_dir / self.get_url_hash(url)
            if cache_path.exists() and self.is_valid(cache_path):
                with cache_path.open('rb') as cache_file:
                    cache = cache_file.read()
        return cache

    def save_cache(self, url, page_source):
        cache_dir = self.get_cache_directory()
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)

        with (cache_dir / self.get_url_hash(url)).open('wb') as cache_file:
            cache_file.write(page_source)

    def get_page_source(self, url, refresh=False):
        """ Gets page source by given url address.
        """

        cache = self.get_cache(url)
        if cache and not refresh:
            page_source = cache
        else:
            request = Request(url, headers=self.get_request_headers())
            page_source = urlopen(request).read()
            self.save_cache(url, page_source)
        return page_source.decode('utf-8')

    def get_locations(self, locations_url, refresh=False):
        locations_page = self.get_page_source(locations_url, refresh=refresh)
        soup = BeautifulSoup(locations_page, 'html.parser')
        locations = []
        for location in soup.find_all('li', attrs={'class': 'drilldown cl'}):
            url = location.find('a').attrs['href']
            location = location.find('em').text
            locations.append((location, url))
        return locations

    def configurate(self, refresh=False):
        locations = self.get_locations(config.ACCU_BROWSE_LOCATIONS,
                                       refresh=refresh)
        while locations:
            for index, location in enumerate(locations):
                print(f'{index + 1}. {location[0]}')

            selected_index = int(input('Please select location: '))
            location = locations[selected_index - 1]
            locations = self.get_locations(location[1], refresh=refresh)

        self.save_configuration(*location)

    def get_weather_info(self, page_content, refresh=False):
        city_page = BeautifulSoup(page_content, 'html.parser')
        current_day_section = city_page.find(
            'li', class_=re.compile('(day|night) current first cl'))

        weather_info = {}
        if current_day_section:
            current_day_url = current_day_section.find('a').attrs['href']
            if current_day_url:
                current_day_page = self.get_page_source(current_day_url,
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
                    feal_temp = weather_details.find('span',
                                                     class_='small-temp')
                    if feal_temp:
                        weather_info['feal_temp'] = feal_temp.text

                    wind_info = weather_details.find_all('li', class_='wind')
                    if wind_info:
                        weather_info['wind'] = \
                            ' '.join(map(lambda t: t.text.strip(), wind_info))

        return weather_info

    def run(self, refresh=False):
        content = self.get_page_source(self.url, refresh=refresh)
        return self.get_weather_info(content, refresh=refresh)
