import sys
import configparser
from pathlib import Path
import logging
from argparse import ArgumentParser

from weatherapp.core.formatters import TableFormatter
from weatherapp.core import config
from weatherapp.core.commandmanager import CommandManager
from weatherapp.core.providermanager import ProviderManager


class App:

    """ Weather aggregator application.
    """

    logger = logging.getLogger(__name__)

    LOG_LEVEL_NAMES = {'WARNING': logging.WARNING,
                       'INFO': logging.INFO,
                       'DEBUG': logging.DEBUG}

    LOG_LEVEL_MAP = {0: logging.WARNING,
                     1: logging.INFO,
                     2: logging.DEBUG}

    def __init__(self, stdin=None, stdout=None, stderr=None):
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.arg_parser = self._arg_parser()
        self.providermanager = ProviderManager()
        self.commandmanager = CommandManager()
        self.formatters = self._load_formatters()

    @staticmethod
    def _arg_parser():
        """ Initialize argument parser.
        """

        arg_parser = ArgumentParser(add_help=False)
        arg_parser.add_argument('command', help='Command', nargs='?')
        arg_parser.add_argument('--refresh', help='Bypass caches',
                                action='store_true')

        arg_parser.add_argument(
            '-f', '--formatter',
            action='store',
            default='table',
            help="Output format, defaults to table")

        arg_parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=config.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output.')

        arg_parser.add_argument(
            '--debug',
            action='store_true',
            default=False,
            help='Show tracebacks on errors.')

        return arg_parser

    @staticmethod
    def _load_formatters():
        return {'table': TableFormatter}

    @staticmethod
    def get_configuration_file():
        return Path.home() / config.CONFIG_FILE

    def configure_logging(self):
        """ Create logging handlers for any log output.
        """

        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.DEBUG)

        console = logging.StreamHandler()
        console_level = logging.WARNING

        configuration = configparser.ConfigParser()
        try:
            configuration.read(self.get_configuration_file())
        except configparser.Error:
            pass
        else:
            if 'App' in configuration.sections():
                app_config = configuration['App']
                log_level = app_config.get('log-level', '')
                if log_level:
                    console_level = self.LOG_LEVEL_NAMES.get(log_level,
                                                             logging.WARNING)

        if self.options.verbose_level:
            console_level = self.LOG_LEVEL_MAP.get(self.options.verbose_level,
                                                   logging.WARNING)
        console.setLevel(console_level)
        formatter = logging.Formatter(config.DEFAULT_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)

    def produce_output(self, title, location, data):
        """ Print results.
        """

        formatter = self.formatters.get(self.options.formatter, 'table')()
        columns = [title, location]

        self.stdout.write(formatter.emit(columns, data))
        self.stdout.write('\n')

    def run_command(self, name, argv):
        """ Run command
        """

        command = self.commandmanager.get(name)
        try:
            command(self).run(argv)
        except Exception:
            msg = "Error during command: %s run"
            if self.options.debug:
                self.logger.exception(msg, name)
            else:
                self.logger.error(msg, name)

    def run_provider(self, name, argv):
        """ Run specified provider
        """

        provider = self.providermanager.get(name)
        if provider:
            provider = provider(self)
            self.produce_output(provider.title,
                                provider.location,
                                provider.run(argv))

    def run_providers(self, argv):
        """ Execute all available providers.
        """

        self.logger.debug("Running all providers.")
        for name, provider in self.providermanager:
            provider = provider(self)
            self.produce_output(provider.title,
                                provider.location,
                                provider.run(argv))

    def run(self, argv):
        """ Run application.

        :param argv: list of passed arguments
        """

        self.options, remaining_args = self.arg_parser.parse_known_args(argv)
        self.configure_logging()

        command_name = self.options.command
        if not command_name:
            # run all providers
            return self.run_providers(remaining_args)

        if command_name in self.commandmanager:
            return self.run_command(command_name, remaining_args)

        if command_name in self.providermanager:
            return self.run_provider(command_name, remaining_args)


def main(argv=sys.argv[1:]):
    return App().run(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
