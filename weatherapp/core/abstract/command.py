import abc
import argparse


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
