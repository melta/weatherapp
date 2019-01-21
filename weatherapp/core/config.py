# application default verbose and log levels
DEFAULT_VERBOSE_LEVEL = 0
DEFAULT_MESSAGE_FORMAT = '%(message)s'

# Fake user agent for weather sites requests
FAKE_MOZILLA_AGENT = 'Mozilla/5.0 (X11; Fedora; Linux x86_64;)'

# Configuration settings
CONFIG_FILE = '.weatherapp.ini'  # configuration file name
CONFIG_LOCATION = 'Location'

# Cache settings
CACHE_DIR = '.wappcache'  # cache directory name
CACHE_TIME = 300          # how long cache files are valid (in seconds)

# entry points group for providers
PROVIDER_EP_NAMESPACE = 'weatherapp.provider'
