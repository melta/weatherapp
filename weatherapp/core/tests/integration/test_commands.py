import unittest
import io

from weatherapp.core.app import App


class CommandsTestCase(unittest.TestCase):

    """ Test case for commands tests.
    """

    def test_providers(self):
        """ Test providers command.
        """

        stdout = io.StringIO()
        App(stdout=stdout).run(['providers'])
        stdout.seek(0)
        self.assertEqual(stdout.read(), 'rp5 \naccu \n')
