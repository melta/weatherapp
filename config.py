# Fake user agent for weather sites requests
FAKE_MOZILLA_AGENT = 'Mozilla/5.0 (X11; Fedora; Linux x86_64;)'

# Configuration settings
CONFIG_FILE = '.weatherapp.ini'  # configuration file name
CONFIG_LOCATION = 'Location'

# Cache settings
CACHE_DIR = '.wappcache'  # cache directory name
CACHE_TIME = 300          # how long cache files are valid (in seconds)


# AccuWeather provider related configuration
ACCU_PROVIDER_NAME = 'accu'          # provider id
ACCU_PROVIDER_TITLE = 'AccuWeather'  # provider title

DEFAULT_ACCU_LOCATION_NAME = 'Lviv'
DEFAULT_ACCU_LOCATION_URL = \
    ('https://www.accuweather.com/uk/ua/lviv/324561/weather-forecast/324561')
ACCU_BROWSE_LOCATIONS = 'https://www.accuweather.com/uk/browse-locations'

# rp5.ua provider related configuration
RP5_PROVIDER_NAME = 'rp5'          # provider id
RP5_PROVIDER_TITLE = 'rp5.ua'      # provider title

DEFAULT_RP5_LOCATION_NAME = 'Lviv'
DEFAULT_RP5_LOCATION_URL = \
    ('http://rp5.ua/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D1%83_%D0%9B%D1%8C%D'
     '0%B2%D0%BE%D0%B2%D1%96,_%D0%9B%D1%8C%D0%B2%D1%96%D0%B2%D1%81%D1%8C%D0%BA'
     '%D0%B0_%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C')
RP5_BROWSE_LOCATIONS = ('http://rp5.ua/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_'
                        '%D0%B2_%D1%81%D0%B2%D1%96%D1%82%D1%96')
