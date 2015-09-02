"""
football scores

"""

import json
import pkg_resources

import requests
import click
from click import echo, secho


class Error(Exception):

    """"""


LIVE_URL = "http://soccer-cli.appspot.com/"

BASE_URL = "http://api.football-data.org/alpha/"
HEADERS = {"X-Auth-Token": ""}
_data = pkg_resources.resource_string("football", "org.football-data.api.json")
leagues, clubs = json.loads(_data.decode("utf-8"))


def print_live_scores():
    """"""
    req = requests.get(LIVE_URL)
    if req.status_code != 200:
        raise Error("There was problem getting live scores")
    scores = req.json()
    if len(scores["games"]) == 0:
        raise Error("No live action currently")
    for game in scores["games"]:
        echo()
        secho("%s\t" % game["league"], fg="green", nl=False)
        if game["goalsHomeTeam"] > game["goalsAwayTeam"]:
            secho("%-20s %-5d" % (game["homeTeamName"], game["goalsHomeTeam"]),
                  bold=True, fg="red", nl=False)
            secho("vs\t", nl=False)
            secho("%d %-10s\t" % (game["goalsAwayTeam"], game["awayTeamName"]),
                  fg="blue", nl=False)
        else:
            secho("%-20s %-5d" % (game["homeTeamName"], game["goalsHomeTeam"]),
                  fg="blue", nl=False)
            secho("vs\t", nl=False)
            secho("%d %-10s\t" % (game["goalsAwayTeam"], game["awayTeamName"]),
                  bold=True, fg="red", nl=False)
        secho("%s" % game["time"], fg="yellow")
        echo()


def print_standings(league):
    """"""
    if not league:
        raise Error("Please specify a league. e.g. `--standings --league=EPL`")
    league_id = leagues[league]
    uri_template = "{base_url}soccerseasons/{id}/leagueTable"
    req = requests.get(uri_template.format(base_url=BASE_URL, id=league_id),
                       headers=HEADERS)
    if req.status_code != 200:
        raise Error("No data for the league. Please check the league code.")
    line_template = ("{position:6}  {club:30}    {played:10}"
                     "    {goaldiff:10}    {points:10}")
    secho(line_template.format(position="POS", club="CLUB",
                               played="PLAYED", goaldiff="GOAL DIFF",
                               points="POINTS"))
    for club in req.json()["standing"]:
        if club["position"] <= 4:
            colors = {"bold": True, "fg": "green"}
        elif 5 <= club["position"] <= 17:
            colors = {"fg": "blue"}
        else:
            colors = {"fg": "red"}
        secho(line_template.format(position=str(club["position"]),
                                   club=str(club["teamName"]),
                                   played=str(club["playedGames"]),
                                   goaldiff=str(club["goalDifference"]),
                                   points=str(club["points"])),
              **colors)


def print_club_scores(club, time):
    """"""
    try:
        club_id = clubs[club][1]
    except KeyError:
        raise Error("No data for the club. Please check the club code.")
    uri_template = "{base_url}teams/{club_id}/fixtures?timeFrame=p{time}"
    req = requests.get(uri_template.format(
        base_url=BASE_URL, club_id=club_id, time=time), headers=HEADERS)
    if req.status_code != 200:
        raise Error("No data for the club. Please check the club code.")
    for score in req.json()["fixtures"]:
        if score["status"] == "FINISHED":
            echo()
            secho("%s\t" % score["date"].split("T")[0], fg="green", nl=False)
            result = score["result"]
            if result["goalsHomeTeam"] > result["goalsAwayTeam"]:
                secho("%-20s %-5d" % (score["homeTeamName"],
                                      result["goalsHomeTeam"]),
                      bold=True, fg="red", nl=False)
                secho("vs\t", nl=False)
                secho("%d %-10s\t" % (result["goalsAwayTeam"],
                                      score["awayTeamName"]), fg="blue")
            else:
                secho("%-20s %-5d" % (score["homeTeamName"],
                                      result["goalsHomeTeam"]),
                      fg="blue", nl=False)
                secho("vs\t", nl=False)
                secho("%d %-10s\t" % (result["goalsAwayTeam"],
                                      score["awayTeamName"]),
                      bold=True, fg="red")
            echo()


def print_league_scores(league, time):
    """"""
    if league:
        league_id = leagues[league]
        uri = "{base_url}soccerseasons/{id}/fixtures?timeFrame=p{time}"
        req = requests.get(uri.format(base_url=BASE_URL, id=league_id,
                                      time=str(time)), headers=HEADERS)
    else:
        uri = "{base_url}fixtures?timeFrame=p{time}"
        req = requests.get(uri.format(base_url=BASE_URL, time=str(time)),
                           headers=HEADERS)
    for data in req.json()["fixtures"]:
        if data["result"]["goalsHomeTeam"] > data["result"]["goalsAwayTeam"]:
            secho("%-20s %-5d" % (data["homeTeamName"],
                                  data["result"]["goalsHomeTeam"]),
                  bold=True, fg="red", nl=False)
            secho("vs\t", nl=False)
            secho("%d %-10s\t" % (data["result"]["goalsAwayTeam"],
                                  data["awayTeamName"]), fg="blue")
        else:
            secho("%-20s %-5d" % (data["homeTeamName"],
                                  data["result"]["goalsHomeTeam"]),
                  fg="blue", nl=False)
            secho("vs\t", nl=False)
            secho("%d %-10s\t" % (data["result"]["goalsAwayTeam"],
                                  data["awayTeamName"]),
                  bold=True, fg="red")
        echo()


@click.command()
@click.option("--live", is_flag=True,
              help="Shows live scores from various leagues")
@click.option("-s", "--standings", is_flag=True,
              help="Standings for a particular league")
@click.option("-l", "--league", type=click.Choice(leagues.keys()),
              help="Choose the league whose fixtures you want to see: "
                   "Bundesliga (BL), Premier League (EPL), La Liga (LLIGA),"
                   "Serie A (SL), Ligue 1(FL), Eredivisie (DED), "
                   "Primeira Liga (PPL)")
@click.option("-c", "--club", type=click.Choice(clubs.keys()),
              help="Choose the club whose fixtures you want to see.")
@click.option("--time", default=6,
              help="The number of days for which you want to see the scores")
@click.option("--auth", default="", help="Auth token")
def main(league, time, standings, club, live, auth):
    """
    print live and past football scores from various international leagues

    """
    global HEADERS
    HEADERS["X-Auth-Token"] = auth
    try:
        if live:
            print_live_scores()
        elif standings:
            print_standings(league)
        elif club:
            print_club_scores(club, time)
        else:
            print_league_scores(league, time)
    except Error as err:
        secho(err.args[0], fg="red", bold=True)


if __name__ == "__main__":
    main()
