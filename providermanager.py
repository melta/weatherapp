from providers import AccuWeatherProvider


class ProviderManager:

    """ Discovers registered providers and loads them.
    """

    def __init__(self):
        self._providers = {}
        self._load_providers()

    def _load_providers(self):
        """ Loads all existing providers.
        """

        for provider in [AccuWeatherProvider]:
            self.add(provider)

    def add(self, provider):
        """ Add provider.
        """
        self._providers[provider().name] = provider

    def get(self, name):
        """ Get provider by name.
        """

        return self._providers.get(name, None)

    def __iter__(self):
        return self._providers.items()

    def __contains__(self, name):
        return name in self._providers
