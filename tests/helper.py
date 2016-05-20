import betamax
import os
import sys
import pytest
import unittest
import soccer.main
import soccer.writers
from click.testing import CliRunner


@pytest.mark.usefixtures('betamax_simple_body')
class IntegrationHelper(unittest.TestCase):
    def setUp(self):
        self.session = soccer.main.session
        self.recorder = betamax.Betamax(self.session)

        self.cli_runner = CliRunner()
        self.writer = soccer.writers.get_writer('stdout')
        soccer.main.headers['X-Auth-Token'] = soccer.main.load_config_key()

    def cassette_name(self, method, cls=None):
        class_name = cls or self.described_class
        return '_'.join([class_name, method])

    def get_output(self, out):
        sys.stdout.flush()
        return out.getvalue()

    @property
    def described_class(self):
        class_name = self.__class__.__name__
        return class_name[4:]
