""" Abstract classes for project
"""

import abc
import time
import hashlib
import argparse
import configparser
from pathlib import Path

import requests

import config


class Command(abc.ABC):

    """ Base class for commands.

    :param app: Main application instance
    :type app: `app.App`
    """

    def __init__(self, app):
        self.app = app

    @staticmethod
    def get_parser():
        """ Initialize argument parser for command.
        """
        parser = argparse.ArgumentParser()
        return parser

    @abc.abstractmethod
    def run(self, argv):
        """ Invoked by application when the command is run.

        Should be overriden in subclass.
        """


class WeatherProvider(Command):

    """ Weather provider abstract class.

    Defines behavior for all weather providers.
    """

    def __init__(self, app):
        super().__init__(app)

        location, url = self._get_configuration()
        self.location = location
        self.url = url

    @abc.abstractmethod
    def get_name(self):
        """ Provider name
        """

    @abc.abstractmethod
    def get_default_location(self):
        """ Default location name
        """

    @abc.abstractmethod
    def get_default_url(self):
        """ Defalt location url
        """

    @abc.abstractmethod
    def configurate(self):
        """ Performs provider configuration.
        """

    @abc.abstractmethod
    def get_weather_info(self, content):
        """ Collects weather information.

        Gets weather information from source and produce it in
        the following format.

        weather_info = {
            'cond':        ''  # weather condition
            'temp':        ''  # temperature
            'feels_like':  ''  # feels like temperature
            'wind':        ''  # information about wind
        }
        """

    @staticmethod
    def get_configuration_file():
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

        name = self.get_default_location()
        url = self.get_default_url()
        configuration = configparser.ConfigParser()

        try:
            configuration.read(self.get_configuration_file())
        except configparser.Error:
            print((f"Bad configuration file. "
                   f"Please reconfigurate your provider: {self.get_name()}"))

        if self.get_name() in configuration.sections():
            location_config = configuration[self.get_name()]
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
        config_file = self.get_configuration_file()

        if config_file.exists():
            parser.read(config_file)

        parser[self.get_name()] = {'name': name, 'url': url}
        with open(config_file, 'w') as configfile:
            parser.write(configfile)

    @staticmethod
    def get_request_headers():
        """ Return custom headers for url requests.
        """

        return {'User-Agent': config.FAKE_MOZILLA_AGENT}

    @staticmethod
    def get_url_hash(url):
        """ Generate url hash.
        """

        return hashlib.md5(url.encode('utf-8')).hexdigest()

    @staticmethod
    def get_cache_directory():
        """ Return home directory for cache files.
        """

        return Path.home() / config.CACHE_DIR

    @staticmethod
    def is_valid(path):
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
        """ Save cache.
        """
        cache_dir = self.get_cache_directory()
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True)

        with (cache_dir / self.get_url_hash(url)).open('wb') as cache_file:
            cache_file.write(page_source)

    def get_page_source(self, url):
        """ Gets page source by given url address.
        """

        cache = self.get_cache(url)
        if cache and not self.app.options.refresh:
            page_source = cache
        else:
            page = requests.get(url, headers=self.get_request_headers())
            page_source = page.content
            self.save_cache(url, page_source)
        return page_source.decode('utf-8')

    def run(self, argv):
        """ Run provider.
        """

        content = self.get_page_source(self.url)
        return self.get_weather_info(content)


class Manager(abc.ABC):

    """ Abstract class for project command managers.
    """

    @abc.abstractmethod
    def add(self, name, command):
        """ Add new command to manager.

        :param name: command name
        :type name: str
        :param command: command class
        :type command: Sub type of `weatherapp.abstract.Command`

        """

    @abc.abstractmethod
    def get(self, name):
        """ Get command from manager by name.

        :param name: command name
        :type name: str
        """

    @abc.abstractmethod
    def __getitem__(self, name):
        """ Get command by name.

        Implementation of this 'dunder' method allow us to access commands
        by name in the same way at it works in dictionary.

        :param name: command name
        :type name: str
        """

    @abc.abstractmethod
    def __contains__(self, name):
        """ Check if command with provided name is in manager.

        Implementation of this 'dunder' method allow us to use 'in' operator
        with manager to check if command exists in manager.

        :param name: command name
        :type name: str
        """
