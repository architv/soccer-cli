import unittest
import soccer.main
import soccer.writers
from .helper import IntegrationHelper

class TestScores(IntegrationHelper):
	def test_live(self):
		cassette_name = self.cassette_name('live_games')
		with self.recorder.use_cassette(cassette_name):
			writer = soccer.writers.get_writer('stdout')
			soccer.main.session = self.session
			soccer.main.get_live_scores(writer, False)
