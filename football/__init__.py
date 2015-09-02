"""
football scores

"""

import json
from pkg_resources import resource_string

import requests
import click


LIVE_URL = "http://soccer-cli.appspot.com/"
BASE_URL = "http://api.football-data.org/alpha/"
HEADERS = {"X-Auth-Token": ""}

leauges = {"BL": 394,
           "FL": 396,
           "EPL": 398,
           "LLIGA": 399,
           "SA": 401,
           "PPL": 402,
           "DED": 404}
teams = json.loads(resource_string("football", "clubs.json").decode("utf-8"))


def get_live_scores():
    """
    gets the live scores

    """
    req = requests.get(LIVE_URL)
    if req.status_code == 200:
        scores = req.json()
        if len(scores["games"]) == 0:
            click.secho("No live action currently", fg="red", bold=True)
            return
        print_live_scores(scores)
    else:
        click.secho("There was problem getting live scores",
                    fg="red", bold=True)


def print_live_scores(live_scores):
    """
    prints the live scores in a pretty format

    """
    for game in live_scores["games"]:
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


def get_team_scores(team, time):
    """
    queries the API and gets the particular team scores

    """
    try:
        team_id = teams[team][1]
    except KeyError:
        click.secho("No data for the team. Please check the team code.",
                    fg="red", bold=True)
    if team_id:
        uri_template = "{base_url}teams/{team_id}/fixtures?timeFrame=p{time}"
        req = requests.get(uri_template.format(
            base_url=BASE_URL, team_id=team_id, time=time), headers=HEADERS)
        if req.status_code == 200:
            print_team_scores(req.json())
        else:
            click.secho("No data for the team. Please check the team code.",
                        fg="red", bold=True)


def print_team_scores(team_scores):
    """
    prints the teams scores in a pretty format

    """
    for score in team_scores["fixtures"]:
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


def get_standings(league):
    """
    queries the API and gets the standings for a particular league

    """
    if not league:
        click.secho("Please specify a league. e.g. `--standings --league=EPL`",
                    fg="red", bold=True)
        return

    league_id = leauges[league]
    uri_template = "{base_url}soccerseasons/{id}/leagueTable"
    req = requests.get(uri_template.format(base_url=BASE_URL, id=league_id),
                       headers=HEADERS)
    if req.status_code == 200:
        print_standings(req.json())
    else:
        click.secho("No data for the league. Please check the league code.",
                    fg="red", bold=True)


def print_standings(league_table):
    """
    prints the league standings in a pretty way

    """
    line_template = ("{position:6}  {team:30}    {played:10}"
                     "    {goaldiff:10}    {points:10}")
    click.secho(line_template.format(position="POS", team="CLUB",
                                     played="PLAYED", goaldiff="GOAL DIFF",
                                     points="POINTS"))
    for team in league_table["standing"]:
        if team["position"] <= 4:
            colors = {"bold": True, "fg": "green"}
        elif 5 <= team["position"] <= 17:
            colors = {"fg": "blue"}
        else:
            colors = {"fg": "red"}
        click.secho(line_template.format(position=str(team["position"]),
                                         team=str(team["teamName"]),
                                         played=str(team["playedGames"]),
                                         goaldiff=str(team["goalDifference"]),
                                         points=str(team["points"])),
                    **colors)


def get_scores(league, time):
    """
    fetch scores based upon league and time

    """
    if league:
        league_id = leauges[league]
        uri_template = ("{base_url}soccerseasons/{id}/"
                        "fixtures?timeFrame=p{time}")
        results = requests.get(uri_template.format(base_url=BASE_URL,
                                                   id=league_id,
                                                   time=str(time)),
                               headers=HEADERS).json()
        print_league_scores(results)
        return
    uri_template = "{base_url}fixtures?timeFrame=p{time}"
    results = requests.get(uri_template.format(base_url=BASE_URL,
                                               time=str(time)),
                           headers=HEADERS).json()
    print_league_scores(results)


def print_league_scores(total_data):
    """
    prints the data in a pretty format

    """
    for data in total_data["fixtures"]:
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
@click.option("-l", "--league", type=click.Choice(leauges.keys()),
              help="Choose the league whose fixtures you want to see. "
                   "Bundesliga(BL), Premier League(EPL), La Liga (LLIGA),"
                   "Serie A(SL), Ligue 1(FL), Eredivisie(DED), "
                   "Primeira Liga(PPL))")
@click.option("-t", "--team", type=click.Choice(teams.keys()),
              help="Choose the team whose fixtures you want to see. See "
                   "the various team codes listed on README)")
@click.option("--time", default=6,
              help="The number of days for which you want to see the scores")
@click.option("--auth", default="", help="Auth token")
def main(league, time, standings, team, live, auth):
    """
    a CLI for live and past football scores from various football leagues

    """
    global HEADERS
    HEADERS["X-Auth-Token"] = auth

    if live:
        get_live_scores()
        return
    if standings:
        get_standings(league)
        return
    if team:
        get_team_scores(team, time)
        return
    get_scores(league, time)


if __name__ == "__main__":
    main()
