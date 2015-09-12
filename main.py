#!/usr/bin/env python

import click
import json
import requests

import authtoken
import leagueids
import leagueproperties
import teamnames

from itertools import groupby

BASE_URL = 'http://api.football-data.org/alpha/'
LIVE_URL = 'http://soccer-cli.appspot.com/'
LEAGUE_IDS = leagueids.LEAGUE_IDS
TEAM_NAMES = teamnames.team_names
LEAGUE_PROPERTIES = leagueproperties.LEAGUE_PROPERTIES

headers = {
    'X-Auth-Token': authtoken.API_TOKEN
}


def get_live_scores():
    """ Gets the live scores """

    req = requests.get(LIVE_URL)
    if req.status_code == requests.codes.ok:
        scores = req.json()
        if len(scores["games"]) == 0:
            click.secho("No live action currently", fg="red", bold=True)
            return
        print_live_scores(scores)
    else:
        click.secho("There was problem getting live scores", fg="red", bold=True)


def print_live_scores(live_scores):
    """ Prints the live scores in a pretty format """

    for game in live_scores["games"]:
        click.echo()
        click.secho("%s\t" % game["league"], fg="green", nl=False)
        if game["goalsHomeTeam"] > game["goalsAwayTeam"]:
            click.secho('%-20s %-5d' % (game["homeTeamName"], game["goalsHomeTeam"]),
                bold=True, fg="red", nl=False)
            click.secho("vs\t", nl=False)
            click.secho('%d %-10s\t' % (game["goalsAwayTeam"], game["awayTeamName"]),
                fg="blue", nl=False)
        else:
            click.secho('%-20s %-5d' % (game["homeTeamName"], game["goalsHomeTeam"]),
                fg="blue", nl=False)
            click.secho("vs\t", nl=False)
            click.secho('%d %-10s\t' % (game["goalsAwayTeam"], game["awayTeamName"]),
                bold=True, fg="red", nl=False)
        click.secho('%s' % game["time"], fg="yellow")
        click.echo()


def get_team_scores(team, time):
    """ Queries the API and gets the particular team scores """

    team_id = TEAM_NAMES.get(team, None)
    if team_id:
        req = requests.get('{base_url}teams/{team_id}/fixtures?timeFrame=p{time}'.format(
            base_url=BASE_URL, team_id=team_id, time=time), headers=headers)
        if req.status_code == requests.codes.ok:
            team_scores = req.json()
            if len(team_scores["fixtures"]) == 0:
                click.secho("No action during past week. Change the time \
                    parameter to get more fixtures.", fg="red", bold=True)
            else:
                print_team_scores(team_scores)
        else:
            click.secho("No data for the team. Please check the team code.",
                fg="red", bold=True)
    else:
        click.secho("No data for the team. Please check the team code.",
            fg="red", bold=True)


def print_team_scores(team_scores):
    """ Prints the teams scores in a pretty format """

    for score in team_scores["fixtures"]:
        if score["status"] == "FINISHED":
            click.echo()
            click.secho("%s\t" % score["date"].split('T')[0], fg="green", nl=False)
            if score["result"]["goalsHomeTeam"] > score["result"]["goalsAwayTeam"]:
                click.secho('%-20s %-5d' % (score["homeTeamName"], 
                    score["result"]["goalsHomeTeam"]), bold=True, fg="red", nl=False)
                click.secho("vs\t", nl=False)
                click.secho('%d %-10s\t' % (score["result"]["goalsAwayTeam"], 
                    score["awayTeamName"]), fg="blue")
            elif score["result"]["goalsHomeTeam"] < score["result"]["goalsAwayTeam"]:
                click.secho('%-20s %-5d' % (score["homeTeamName"], 
                    score["result"]["goalsHomeTeam"]), fg="blue", nl=False)
                click.secho("vs\t", nl=False)
                click.secho('%d %-10s\t' % (score["result"]["goalsAwayTeam"], 
                    score["awayTeamName"]), bold=True, fg="red")
            else:
                click.secho('%-20s %-5d' % (score["homeTeamName"], 
                    score["result"]["goalsHomeTeam"]), bold=True, fg="yellow", nl=False)
                click.secho("vs\t", nl=False)
                click.secho('%d %-10s\t' % (score["result"]["goalsAwayTeam"], 
                    score["awayTeamName"]), bold=True, fg="yellow")
            click.echo()


def get_standings(league):
    """ Queries the API and gets the standings for a particular league """

    if not league:
        click.secho("Please specify a league. Example --standings --league=EPL",
            fg="red", bold=True)
        return

    league_id = LEAGUE_IDS[league]
    req = requests.get('{base_url}soccerseasons/{id}/leagueTable'.format(
            base_url=BASE_URL, id=league_id), headers=headers)
    if req.status_code == requests.codes.ok:
        print_standings(req.json(), league)
    else:
        click.secho("No standings availble for {league}.".format(league=league),
            fg="red", bold=True)


def print_standings(league_table, league):
    """ Prints the league standings in a pretty way """

    click.secho("%-6s  %-30s    %-10s    %-10s    %-10s" %
                ("POS", "CLUB", "PLAYED", "GOAL DIFF", "POINTS"))
    positionlist = [team["position"] for team in league_table["standing"]]
    for team in league_table["standing"]:
        if team["goalDifference"] >= 0:
            team["goalDifference"] = ' ' + str(team["goalDifference"])
        if LEAGUE_PROPERTIES[league]["cl"][0] <= team["position"] <= LEAGUE_PROPERTIES[league]["cl"][1]:
            click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
                (str(team["position"]), team["teamName"],
                str(team["playedGames"]), team["goalDifference"],str(team["points"])),
                bold=True, fg="green")
        elif LEAGUE_PROPERTIES[league]["el"][0] <= team["position"] <= LEAGUE_PROPERTIES[league]["el"][1]:
            click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
                (str(team["position"]), team["teamName"],
                str(team["playedGames"]), team["goalDifference"],str(team["points"])),
                fg="yellow")
        elif LEAGUE_PROPERTIES[league]["rl"][0] <= team["position"] <= LEAGUE_PROPERTIES[league]["rl"][1]:  # 5-15 in BL, 5-17 in others
            click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
                (str(team["position"]), team["teamName"],
                str(team["playedGames"]), team["goalDifference"],str(team["points"])),
                fg="red")
        else:
            click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
                (str(team["position"]), team["teamName"],
                str(team["playedGames"]), team["goalDifference"],str(team["points"])),
                fg="blue")


def get_scores(league, time):
    """ Queries the API and fetches the scores for fixtures
    based upon the league and time parameter """

    if league:
        league_id = LEAGUE_IDS[league]
        req = requests.get('{base_url}soccerseasons/{id}/fixtures?timeFrame=p{time}'.format(
            base_url=BASE_URL, id=league_id, time=str(time)), headers=headers)
        if req.status_code == requests.codes.ok:
            fixtures_results = req.json()
            # no fixtures in the past wee. display a help message and return
            if len(fixtures_results["fixtures"]) == 0:
                click.secho("No {league} matches in the past week.".format(league=league),
                    fg="red", bold=True)
            else:
                print_league_scores(fixtures_results)
        else:
            click.secho("No data for the given league",
                fg="red", bold=True)
        return

    req = requests.get('{base_url}fixtures?timeFrame=p{time}'.format(
        base_url=BASE_URL, time=str(time)), headers=headers)
    if req.status_code == requests.codes.ok:
            fixtures_results = req.json()
            print_league_scores(fixtures_results)


def supported_leagues(total_data):
    """ Filters out scores of unsupported leagues """

    supported_leagues = {val: key for key, val in LEAGUE_IDS.items()}

    get_league_id = lambda x: int(x["_links"]["soccerseason"]["href"].split("/")[-1])
    fixtures = (fixture for fixture in total_data["fixtures"]
                if get_league_id(fixture) in supported_leagues)

    # Sort the scores by league to make it easier to read
    fixtures = sorted(fixtures, key=get_league_id)
    for league, scores in groupby(fixtures, key=get_league_id):
        
        # Print league header
        league_name = " {0} ".format(supported_leagues[league])
        click.echo()
        click.secho("{:=^56}".format(league_name), fg="green")
        click.echo()

        for score in scores:
            yield score


def print_league_scores(total_data):
    """ Prints the data in a pretty format """

    for data in supported_leagues(total_data):
        if data["result"]["goalsHomeTeam"] > data["result"]["goalsAwayTeam"]:
            click.secho('%-20s %-5d' % (data["homeTeamName"], 
                data["result"]["goalsHomeTeam"]),
                bold=True, fg="red", nl=False)
            click.secho("vs\t", nl=False)
            click.secho('%d %-10s\t' % (data["result"]["goalsAwayTeam"], 
                data["awayTeamName"]), fg="blue")
        elif data["result"]["goalsHomeTeam"] < data["result"]["goalsAwayTeam"]:
            click.secho('%-20s %-5d' % (data["homeTeamName"], data["result"]["goalsHomeTeam"]),
                fg="blue", nl=False)
            click.secho("vs\t", nl=False)
            click.secho('%d %-10s\t' % (data["result"]["goalsAwayTeam"], 
                data["awayTeamName"]), bold=True, fg="red")
        else:
            click.secho('%-20s %-5d' % (data["homeTeamName"], data["result"]["goalsHomeTeam"]),
                bold=True, fg="yellow", nl=False)
            click.secho("vs\t", nl=False)
            click.secho('%d %-10s\t' % (data["result"]["goalsAwayTeam"], 
                data["awayTeamName"]), bold=True, fg="yellow")
        click.echo()


@click.command()
@click.option('--live', is_flag=True, help= 'Shows live scores from various leagues')
@click.option('--standings', is_flag=True, help= 'Standings for a particular league')
@click.option('--league', '-league', type=click.Choice(LEAGUE_IDS.keys()),
    help= (
        "Choose the league whose fixtures you want to see. Bundesliga(BL), Premier League(EPL), La Liga (LLIGA),"
        "Serie A(SA), Ligue 1(FL), Eredivisie(DED), Primeira Liga(PPL), Champions League(CL)')"
    )
)
@click.option('--team', type=click.Choice(TEAM_NAMES.keys()),
    help= (
        "Choose the team whose fixtures you want to see. See the various team codes listed on README')"
    )
)
@click.option('--time', default=6,
    help='The number of days in the past for which you want to see the scores')
def main(league, time, standings, team, live):
    """ A CLI for live and past football scores from various football leagues """

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

if __name__ == '__main__':
    main()
