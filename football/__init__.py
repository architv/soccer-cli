"""
football scores

"""

import json
import pkg_resources

import requests
import click


LIVE_URL = "http://soccer-cli.appspot.com/"

BASE_URL = "http://api.football-data.org/alpha/"
HEADERS = {"X-Auth-Token": ""}
_data = pkg_resources.resource_string("football", "org.football-data.api.json")
leagues, clubs = json.loads(_data.decode("utf-8"))


def print_live_scores():
    """"""
    req = requests.get(LIVE_URL)
    if req.status_code != 200:
        click.secho("There was problem getting live scores",
                    fg="red", bold=True)
        return
    scores = req.json()
    if len(scores["games"]) == 0:
        click.secho("No live action currently", fg="red", bold=True)
        return
    for game in scores["games"]:
        click.echo()
        click.secho("%s\t" % game["league"], fg="green", nl=False)
        if game["goalsHomeTeam"] > game["goalsAwayTeam"]:
            click.secho("%-20s %-5d" % (game["homeTeamName"],
                                        game["goalsHomeTeam"]),
                        bold=True, fg="red", nl=False)
            click.secho("vs\t", nl=False)
            click.secho("%d %-10s\t" % (game["goalsAwayTeam"],
                                        game["awayTeamName"]),
                        fg="blue", nl=False)
        else:
            click.secho("%-20s %-5d" % (game["homeTeamName"],
                                        game["goalsHomeTeam"]),
                        fg="blue", nl=False)
            click.secho("vs\t", nl=False)
            click.secho("%d %-10s\t" % (game["goalsAwayTeam"],
                                        game["awayTeamName"]),
                        bold=True, fg="red", nl=False)
        click.secho("%s" % game["time"], fg="yellow")
        click.echo()


def print_club_scores(club, time):
    """"""
    try:
        club_id = clubs[club][1]
    except KeyError:
        click.secho("No data for the club. Please check the club code.",
                    fg="red", bold=True)
    uri_template = "{base_url}teams/{club_id}/fixtures?timeFrame=p{time}"
    req = requests.get(uri_template.format(
        base_url=BASE_URL, club_id=club_id, time=time), headers=HEADERS)
    if req.status_code != 200:
        click.secho("No data for the club. Please check the club code.",
                    fg="red", bold=True)
        return
    for score in req.json()["fixtures"]:
        if score["status"] == "FINISHED":
            click.echo()
            click.secho("%s\t" % score["date"].split("T")[0],
                        fg="green", nl=False)
            result = score["result"]
            if result["goalsHomeTeam"] > result["goalsAwayTeam"]:
                click.secho("%-20s %-5d" % (score["homeTeamName"],
                                            result["goalsHomeTeam"]),
                            bold=True, fg="red", nl=False)
                click.secho("vs\t", nl=False)
                click.secho("%d %-10s\t" % (result["goalsAwayTeam"],
                                            score["awayTeamName"]), fg="blue")
            else:
                click.secho("%-20s %-5d" % (score["homeTeamName"],
                                            result["goalsHomeTeam"]),
                            fg="blue", nl=False)
                click.secho("vs\t", nl=False)
                click.secho("%d %-10s\t" % (result["goalsAwayTeam"],
                                            score["awayTeamName"]),
                            bold=True, fg="red")
            click.echo()


def print_standings(league):
    """"""
    if not league:
        click.secho("Please specify a league. e.g. `--standings --league=EPL`",
                    fg="red", bold=True)
        return

    league_id = leagues[league]
    uri_template = "{base_url}soccerseasons/{id}/leagueTable"
    req = requests.get(uri_template.format(base_url=BASE_URL, id=league_id),
                       headers=HEADERS)
    if req.status_code != 200:
        click.secho("No data for the league. Please check the league code.",
                    fg="red", bold=True)
        return
    line_template = ("{position:6}  {club:30}    {played:10}"
                     "    {goaldiff:10}    {points:10}")
    click.secho(line_template.format(position="POS", club="CLUB",
                                     played="PLAYED", goaldiff="GOAL DIFF",
                                     points="POINTS"))
    for club in req.json()["standing"]:
        if club["position"] <= 4:
            colors = {"bold": True, "fg": "green"}
        elif 5 <= club["position"] <= 17:
            colors = {"fg": "blue"}
        else:
            colors = {"fg": "red"}
        click.secho(line_template.format(position=str(club["position"]),
                                         club=str(club["teamName"]),
                                         played=str(club["playedGames"]),
                                         goaldiff=str(club["goalDifference"]),
                                         points=str(club["points"])),
                    **colors)


def print_scores(league, time):
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
            click.secho("%-20s %-5d" % (data["homeTeamName"],
                                        data["result"]["goalsHomeTeam"]),
                        bold=True, fg="red", nl=False)
            click.secho("vs\t", nl=False)
            click.secho("%d %-10s\t" % (data["result"]["goalsAwayTeam"],
                                        data["awayTeamName"]), fg="blue")
        else:
            click.secho("%-20s %-5d" % (data["homeTeamName"],
                                        data["result"]["goalsHomeTeam"]),
                        fg="blue", nl=False)
            click.secho("vs\t", nl=False)
            click.secho("%d %-10s\t" % (data["result"]["goalsAwayTeam"],
                                        data["awayTeamName"]),
                        bold=True, fg="red")
        click.echo()


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
    a CLI for live and past football scores from various football leagues

    """
    global HEADERS
    HEADERS["X-Auth-Token"] = auth
    if live:
        print_live_scores()
    elif standings:
        print_standings(league)
    elif club:
        print_club_scores(club, time)
    else:
        print_scores(league, time)


if __name__ == "__main__":
    main()
