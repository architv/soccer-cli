import os
import json

def load_json(file):
    """Load JSON file at app start"""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, file)) as jfile:
        data = json.load(jfile)
    return data

TEAM_DATA = load_json("teams.json")["teams"]
TEAM_NAMES = {team["code"]: team["id"] for team in TEAM_DATA}
LEAGUE_DATA = load_json("leagues.json")["leagues"]
LEAGUE_IDS = {league["code"]: league["id"] for league in LEAGUE_DATA}
LEAGUE_PROPERTIES = {league["code"]: league["properties"] for league in LEAGUE_DATA if league["properties"] != "null"}