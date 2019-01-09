from commands import Configurate, Providers

import abstract


class CommandManager(abstract.Manager):

    """ Manager for app commands.
    """

    def __init__(self):
        self._commands = {}
        self._load_commands()

    def add(self, name, command):
        """ Registers command under specified name.

        :param name: command name
        :type name: str
        :param command: command class
        :type command: abstract.Command
        """

        self._commands[name] = command

    def _load_commands(self):
        """Load all external (from an entrypoints) commands."""

        for command in [Configurate, Providers]:
            self.add(command.name, command)

    def get(self, name):
        """ Gets command from command registry.

        Get registered command processor. Returns none if there is no
        such command registered. Raise ValueError if bad command value
        provided.

        :param name: command name from argv
        :type name: str
        """

        return self._commands.get(name, None)

    def __getitem__(self, name):
        return self._commands[name]

    def __contains__(self, name):
        return name in self._commands
