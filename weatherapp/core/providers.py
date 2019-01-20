""" Weather providers.
"""

import urllib

from bs4 import BeautifulSoup

from weatherapp.core import config
from weatherapp.core.abstract import WeatherProvider


class RP5Provider(WeatherProvider):

    """ Provides weather info from rp5.ua site.
    """

    name = config.RP5_PROVIDER_NAME
    title = config.RP5_PROVIDER_TITLE

    def get_name(self):
        return self.name

    def get_default_location(self):
        return config.DEFAULT_RP5_LOCATION_NAME

    def get_default_url(self):
        return config.DEFAULT_RP5_LOCATION_URL

    def get_countries(self, countries_url):
        countries_page = self.get_page_source(countries_url)
        soup = BeautifulSoup(countries_page, 'html.parser')
        base = urllib.parse.urlunsplit(
            urllib.parse.urlparse(countries_url)[:2] + ('/', '', ''))
        countries = []
        for country in soup.find_all('div', class_='country_map_links'):
            url = urllib.parse.urljoin(base, country.find('a').attrs['href'])
            country = country.find('a').text
            countries.append((country, url))
        return countries

    def get_cities(self, country_url):
        cities = []
        cities_page = self.get_page_source(country_url)
        soup = BeautifulSoup(cities_page, 'html.parser')
        base = urllib.parse.urlunsplit(
            urllib.parse.urlparse(country_url)[:2] + ('/', '', ''))
        country_map = soup.find('div', class_='countryMap')
        if country_map:
            cities_list = country_map.find_all('h3')
            for city in cities_list:
                url = urllib.parse.urljoin(base, city.find('a').attrs['href'])
                city = city.find('a').text
                cities.append((city, url))
        return cities

    def configurate(self):
        """ Configure provider.
        """
        countries = self.get_countries(config.RP5_BROWSE_LOCATIONS)
        for index, country in enumerate(countries):
            print(f'{index + 1}. {country[0]}')
        selected_index = int(input('Please select country: '))
        country = countries[selected_index - 1]

        cities = self.get_cities(country[1])
        for index, city in enumerate(cities):
            print(f'{index + 1}. {city[0]}')
        selected_index = int(input('Please select city: '))
        city = cities[selected_index - 1]
        self.save_configuration(*city)

    def get_weather_info(self, page_content):
        """ Collect weather information
        """

        city_page = BeautifulSoup(page_content, 'html.parser')
        current_day = city_page.find('div', id='archiveString')

        weather_info = {'cond': '', 'temp': '', 'feal_temp': '', 'wind': ''}
        if current_day:
            archive_info = current_day.find('div', class_='ArchiveInfo')
            if archive_info:
                archive_text = archive_info.text
                info_list = archive_text.split(',')
                weather_info['cond'] = info_list[1].strip()
                temp = archive_info.find('span', class_='t_0')
                if temp:
                    weather_info['temp'] = temp.text
                wind = info_list[2].strip()[:info_list[2].find(')') + 1]
                wind += info_list[3]
                if wind:
                    weather_info['wind'] = wind

        return weather_info
