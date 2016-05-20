import unittest
import soccer.main
import soccer.writers
from ..helper import IntegrationHelper

class TestLeague(IntegrationHelper):
    def test_team_scores(self):
        cassette_name = self.cassette_name('standings')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as runner:
                league = 'EPL'
                soccer.main.get_standings(league, self.writer)
                header, first, second, _ = self.get_output(runner).split('\n', 3)
                assert 'POS     CLUB                              PLAYED        GOAL DIFF     POINTS    ' == header
                assert '1       Leicester City FC                 33            26            72' == first
                assert '2       Tottenham Hotspur FC              33            35            65' == second
