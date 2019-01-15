from weatherapp.core.providers import AccuWeatherProvider, RP5Provider

from weatherapp.core import commandmanager


class ProviderManager(commandmanager.CommandManager):

    """ Discovers registered providers and loads them.
    """

    def _load_commands(self):
        """ Loads all existing providers.
        """

        for provider in [AccuWeatherProvider, RP5Provider]:
            self.add(provider.name, provider)
