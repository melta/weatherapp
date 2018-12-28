""" App commands
"""

from abstract import Command


class Configurate(Command):

    """ Help to configure weather providers.
    """

    name = 'configurate'

    def get_parser(self):
        parser = super(Configurate, self).get_parser()
        parser.add_argument('provider', help="Provider name")
        return parser

    def run(self, argv):
        """ Run command.
        """

        parsed_args = self.get_parser().parse_args(argv)
        provider_name = parsed_args.provider
        provider_factory = self.app.providermanager.get(provider_name)
        provider_factory(self.app).configurate()


class Providers(Command):

    """ Print all available providers.
    """

    name = 'providers'

    def run(self, argv):
        """ Run command.
        """

        for name in self.app.providermanager._providers:
            print(name)
