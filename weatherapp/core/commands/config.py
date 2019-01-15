from weatherapp.core.abstract import Command


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
