import unittest
import soccer.main
import soccer.writers
from ..helper import IntegrationHelper

class TestScores(IntegrationHelper):
    def test_live(self):
        return
        # TODO: When there are live games
        cassette_name = self.cassette_name('live_games')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as out:
                soccer.main.get_live_scores(self.writer, False)

    def test_specific_league(self):
        cassette_name = self.cassette_name('specific_league')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as runner:
                league = 'EPL'
                time = 6
                show_upcoming = False
                use_12_hour = False
                soccer.main.get_league_scores(league, time, self.writer, show_upcoming, use_12_hour)
                output = self.get_output(runner)
                assert '============================ EPL =============================' == output.split("\n", 1)[0]
                assert 'West Ham United FC         3  vs  3                Arsenal FC' in output
