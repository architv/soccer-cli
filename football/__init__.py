"""
football scores

"""

# TODO name leagues in json file:
#        Bundesliga (BL), Premier League (EPL), La Liga (LLIGA), Serie A (SL),
#        Ligue 1(FL), Eredivisie (DED), Primeira Liga (PPL)

import json
import pkg_resources

import requests
import click
from click import echo, secho


class Error(Exception):

    """"""


LIVE_URI = "http://soccer-cli.appspot.com/"

API_URI = "http://api.football-data.org/alpha/"
AUTH_TOKEN = ""
_data = pkg_resources.resource_string("football", "org.football-data.api.json")
leagues, clubs = json.loads(_data.decode("utf-8"))


def get(path, error):
    req = requests.get(API_URI + path, headers={"X-Auth-Token": AUTH_TOKEN})
    if not req.ok:
        raise Error(error)
    return req.json()


def print_live_scores():
    """"""
    games = get(LIVE_URI, "there was problem getting live scores")["games"]
    if len(games) == 0:
        raise Error("there is currently no live action")
    for game in games:
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


def print_league_standings(league_abbr):
    """"""
    path = "soccerseasons/{}/leagueTable".format(leagues[league_abbr])
    standings = get(path, "no data for given league code")["standing"]
    row_template = "{:3}  {:20}    {:>10}    {:>10}    {:>10}"
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
        path = path_template.format(leagues[league_abbr], duration)
    else:
        path = "fixtures?timeFrame=p{}".format(duration)
    games = get(path, "no data for given league code")["fixtures"]
    for data in games:
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


def print_club_scores(club_abbr, duration):
    """"""
    try:
        club_id = clubs[club_abbr][1]
    except KeyError:
        raise Error("there is no data for given club code")
    path = "teams/{}/fixtures?timeFrame=p{}".format(club_id, duration)
    games = get(path, "no data for given club code")["fixtures"]
    for score in games:
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
    print live and past football scores from various international leagues

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
    except Error as err:
        secho(err.args[0], fg="red", bold=True)


if __name__ == "__main__":
    main()
