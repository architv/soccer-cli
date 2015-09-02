"""
football scores

"""

import json
import pkg_resources

import requests
import click
from click import echo, secho

__all__ = ["print_live_scores", "print_league_standings",
           "print_league_scores", "print_club_scores"]


class RetrievalError(Exception):

    """"""


LIVE_API = "http://soccer-cli.appspot.com/"
PAST_API = "http://api.football-data.org/alpha/"
AUTH_TOKEN = ""
_data = pkg_resources.resource_string("football", "org.football-data.api.json")
leagues, clubs = json.loads(_data.decode("utf-8"))


def print_live_scores():
    """"""
    req = requests.get(LIVE_API)
    if not req.ok:
        raise RetrievalError("problem getting live scores")
    for match in req.json()["games"]:
        secho("%s  " % match["league"], fg="green", nl=False)
        _print_match(match)
        secho("%s" % match["time"], fg="yellow")
        echo()


def print_league_standings(league_abbr):
    """"""
    path = "soccerseasons/{}/leagueTable".format(leagues[league_abbr][1])
    standings = _get_api(path, "no data for given league code")["standing"]
    row_template = "{:3}  {:25}    {:>10}    {:>10}    {:>10}"
    secho(row_template.format("POS", "CLUB", "PLAYED", "GOAL DIFF", "POINTS"))
    for club in standings:
        if club["position"] <= 4:
            colors = {"bold": True, "fg": "green"}
        elif 5 <= club["position"] <= 17:
            colors = {"fg": "blue"}
        else:
            colors = {"fg": "red"}
        secho(row_template.format(club["position"], club["teamName"],
                                  club["playedGames"], club["goalDifference"],
                                  club["points"]), **colors)


def print_league_scores(league_abbr, duration):
    """"""
    if league_abbr:
        path_template = "soccerseasons/{}/fixtures?timeFrame=p{}"
        path = path_template.format(leagues[league_abbr][1], duration)
    else:
        path = "fixtures?timeFrame=p{}".format(duration)
    for match in _get_api(path, "no data for given league code")["fixtures"]:
        _print_match(match)


def print_club_scores(club_abbr, duration):
    """"""
    try:
        club_id = clubs[club_abbr][1]
    except KeyError:
        raise RetrievalError("no data for given club code")
    path = "teams/{}/fixtures?timeFrame=p{}".format(club_id, duration)
    for match in _get_api(path, "no data for given club code")["fixtures"]:
        _print_match(match)


def _print_match(match):
    result = match["result"]
    home_colors = {"bold": True, "fg": "red"}
    away_colors = {"fg": "blue"}
    if result["goalsHomeTeam"] < result["goalsAwayTeam"]:
        home_colors, away_colors = away_colors, home_colors
    home_club, away_club = match["homeTeamName"], match["awayTeamName"]
    home_goals, away_goals = result["goalsHomeTeam"], result["goalsAwayTeam"]

    secho("{:25} {:5}".format(home_club, home_goals), nl=False, **home_colors)
    secho(" vs ", nl=False)
    secho("{} {:25}".format(away_goals, away_club), **away_colors)
    echo()


def _get_api(path, error):
    req = requests.get(PAST_API + path, headers={"X-Auth-Token": AUTH_TOKEN})
    if not req.ok:
        raise RetrievalError(error)
    return req.json()


@click.command()
@click.option("--live", is_flag=True,
              help="view live scores from current games")
@click.option("-s", "--standings", is_flag=True,
              help="view standings for a particular league")
@click.option("-l", "--league", type=click.Choice(leagues))
@click.option("-c", "--club", type=click.Choice(clubs))
@click.option("--duration", default=6, help="narrow to number of past days")
@click.option("--auth", default="", help="football-data.org API token")
def main(league, duration, standings, club, live, auth):
    """
    print live and past scores from various international football leagues

    """
    global AUTH_TOKEN
    AUTH_TOKEN = auth
    try:
        if live:
            print_live_scores()
        elif standings:
            print_league_standings(league)
        elif club:
            print_club_scores(club, duration)
        else:
            print_league_scores(league, duration)
    except RetrievalError as err:
        secho(err.args[0], fg="red", bold=True)


if __name__ == "__main__":
    main()
