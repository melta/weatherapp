import sys
from argparse import ArgumentParser

from providermanager import ProviderManager


class App:

    """ Weather aggregator application.
    """

    def __init__(self):
        self.arg_parser = self._arg_parser()
        self.providermanager = ProviderManager()

    def _arg_parser(self):
        """
        """
        arg_parser = ArgumentParser(add_help=False)
        arg_parser.add_argument('command', help='Command', nargs='?')
        return arg_parser

    def run(self, argv):
        """ Run application.

        :param argv: list of passed arguments
        """

        self.options, remaining_args = self.arg_parser.parse_known_args(argv)
        command_name = self.options.command



def main(argv=sys.argv[1:]):
    return App().run(argv)
