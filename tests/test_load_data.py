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
        raised = False
        try:
            load_json(TestLoadData.TEAMS_INFO_FILENAME)["teams"]
        except IOError:
            raised = True
        self.assertFalse(raised)

    def test_load_league_properties(self):
        raised = False
        try:
            league_properties = leagueproperties.LEAGUE_PROPERTIES
            league_properties.keys()
        except AttributeError:
            raised = True
        self.assertFalse(raised)

    def test_load_league_ids(self):
        raised = False
        try:
            leage_ids = leagueids.LEAGUE_IDS
            leage_ids.keys()
        except AttributeError:
            raised = True
        self.assertFalse(raised)


if __name__ == '__main__':
    unittest.main()
