import unittest
import soccer.main
import soccer.writers
from .helper import IntegrationHelper

class TestScores(IntegrationHelper):
    def test_live(self):
        # TODO: When there are live games
        cassette_name = self.cassette_name('live_games')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as out:
                soccer.main.get_live_scores(self.writer, False)
