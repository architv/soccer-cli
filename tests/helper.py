import betamax
import os
import pytest
import unittest
from soccer.main import session


@pytest.mark.usefixtures('betamax_simple_body')
class IntegrationHelper(unittest.TestCase):
    def setUp(self):
        self.session = session
        self.recorder = betamax.Betamax(self.session)

    def cassette_name(self, method, cls=None):
        class_name = cls or self.described_class
        return '_'.join([class_name, method])

    @property
    def described_class(self):
        class_name = self.__class__.__name__
        return class_name[4:]