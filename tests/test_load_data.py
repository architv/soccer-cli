import unittest
import sys

sys.path.append('soccer')

from soccer import leagueproperties
from soccer import leagueids
from soccer.main import load_json


class TestLoadData(unittest.TestCase):

    TEAMS_INFO_FILENAME = "teams.json"

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def test_load_team_data(self):
        try:
            load_json(TestLoadData.TEAMS_INFO_FILENAME)["teams"]
        except IOError:
            self.fail("File doesn't exist!")

    def test_load_league_properties(self):
        try:
            league_properties = leagueproperties.LEAGUE_PROPERTIES
        except AttributeError:
            self.fail("File doesn't exist!")

    def test_load_league_ids(self):
        try:
            leage_ids = leagueids.LEAGUE_IDS
            leage_ids.keys()
        except AttributeError:
            self.fail("File doesn't exist!")


if __name__ == '__main__':
    unittest.main()
