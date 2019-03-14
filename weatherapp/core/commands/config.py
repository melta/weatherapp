import configparser
from pathlib import Path

from weatherapp.core import config
from weatherapp.core.abstract import Command


class Configurate(Command):

    """ Help to configure weather providers.
    """

    name = 'configurate'

    def get_parser(self):
        parser = super(Configurate, self).get_parser()
        parser.add_argument('provider', help="Provider name", nargs="?")
        parser.add_argument(
            '-l', '--log-level',
            dest='log_level',
            help="Application log level")
        return parser

    def save_log_configuration(self, loglevel):
        """ Save log level for application. """

        parser = configparser.ConfigParser()
        config_file = Path.home() / config.CONFIG_FILE

        if config_file.exists():
            parser.read(config_file)

        parser['App'] = {'log-level': loglevel}
        with open(config_file, 'w') as configfile:
            parser.write(configfile)

    def run(self, argv):
        """ Run command.
        """

        parsed_args = self.get_parser().parse_args(argv)
        if parsed_args.log_level:
            self.save_log_configuration(parsed_args.log_level)

        if parsed_args.provider:
            provider_name = parsed_args.provider
            provider_factory = self.app.providermanager.get(provider_name)
            provider_factory(self.app).configurate()
