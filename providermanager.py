from providers import AccuWeatherProvider, RP5Provider


class ProviderManager:

    """ Discovers registered providers and loads them.
    """

    def __init__(self):
        self._providers = {}
        self._load_providers()

    def _load_providers(self):
        """ Loads all existing providers.
        """

        for provider in [AccuWeatherProvider, RP5Provider]:
            self.add(provider.name, provider)

    def add(self, name, provider):
        """ Add provider.
        """
        self._providers[name] = provider

    def get(self, name):
        """ Get provider by name.
        """

        return self._providers.get(name, None)

    def __getitem__(self, name):
        return self._providers[name]

    def __contains__(self, name):
        return name in self._providers
