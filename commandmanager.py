from commands import Configurate, Providers


class CommandManager:

    """ Manager for app commands.
    """

    def __init__(self):
        self.commands = {}
        self._load_commands()

    def add(self, name, command):
        """ Registers command under specified name.

        :param name: command name
        :type name: str
        :param command: command class
        :type command: abstract.Command
        """

        self.commands[name] = command

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

        return self.commands.get(name, None)

    def __contains__(self, name):
        return name in self.commands
