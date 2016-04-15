# -*- coding: utf-8 -*- 
import unittest
import soccer.main
import soccer.writers
from ..helper import IntegrationHelper

class TestTeam(IntegrationHelper):
    def test_team_scores(self):
        cassette_name = self.cassette_name('scores')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as runner:
                team = 'AFC'
                time = 6
                use12hour = True
                upcoming = False
                soccer.main.get_team_scores(team, time, self.writer, upcoming, use12hour)
                assert self.get_output(runner) == '\n2016-04-09\tWest Ham United FC         3  vs  3                Arsenal FC\n'

    def test_incorrect_team(self):
        cassette_name = self.cassette_name('invalid')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as runner:
                team = 'INVALIDTEAM'
                time = 6
                use12hour = True
                upcoming = False
                soccer.main.get_team_scores(team, time, self.writer, upcoming, use12hour)
                assert self.get_output(runner) == 'Team code is not correct.\n'

    def test_team_upcoming_games_with_utc_time(self):
        cassette_name = self.cassette_name('upcoming_games')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as runner:
                team = 'AFC'
                time = 6
                use12hour = False
                upcoming = True
                soccer.main.get_team_scores(team, time, self.writer, upcoming, use12hour)
                assert self.get_output(runner) == '\nArsenal FC                 -  vs  -         Crystal Palace FC   Sun 17, 08:00\n'

    def test_team_upcoming_games_with_local_time(self):
        cassette_name = self.cassette_name('upcoming_games')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as runner:
                team = 'AFC'
                time = 6
                use12hour = True
                upcoming = True
                soccer.main.get_team_scores(team, time, self.writer, upcoming, use12hour)
                assert self.get_output(runner) == '\nArsenal FC                 -  vs  -         Crystal Palace FC   Sun 17, 08:00 AM\n'

    def test_team_player_names(self):
        cassette_name = self.cassette_name('player_names')
        with self.recorder.use_cassette(cassette_name):
            with self.cli_runner.isolation() as runner:
                team = 'AFC'
                soccer.main.get_team_players(team, self.writer)
                output = self.get_output(runner)
                assert 'N.   NAME                         POSITION                NATIONALITY             BIRTHDAY           MARKET VALUE' in output
                assert u'11   Mesut Özil                   Attacking Midfield      Germany                 1988-10-15         40,000,000' in unicode(output, 'utf-8')


