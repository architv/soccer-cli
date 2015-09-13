#!/usr/bin/env python

import click
import csv
import datetime
import json
import os
import requests
import sys

import leagueids
import leagueproperties
import teamnames

from itertools import groupby

BASE_URL = 'http://api.football-data.org/alpha/'
LIVE_URL = 'http://soccer-cli.appspot.com/'
LEAGUE_IDS = leagueids.LEAGUE_IDS
TEAM_NAMES = teamnames.team_names
LEAGUE_PROPERTIES = leagueproperties.LEAGUE_PROPERTIES

try:
    api_token = os.environ.get('SOCCER_CLI_API_TOKEN')
except:
    from config import config
    api_token = config.get('SOCCER_CLI_API_TOKEN')

if not api_token:
    print ('No API Token detected. Please visit {0} and get an API Token, '
           'which will be used by the Soccer CLI to get access to the data'
           .format(BASE_URL))
    sys.exit(1)

headers = {
    'X-Auth-Token': api_token
}


def get_live_scores(output):
    """Gets the live scores"""
    req = requests.get(LIVE_URL)
    if req.status_code == requests.codes.ok:
        scores = req.json()
        if len(scores["games"]) == 0:
            click.secho("No live action currently", fg="red", bold=True)
            return
        globals()[output + '_live_scores'](scores)
    else:
        click.secho("There was problem getting live scores", fg="red", bold=True)


def stdout_live_scores(live_scores):
    """Prints the live scores in a pretty format"""
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

def csv_live_scores(live_scores):
    """Store output of live scores to a CSV file"""
    today_datetime = datetime.datetime.now()
    today_date = '_'.join([str(today_datetime.year), str(today_datetime.month),
                           str(today_datetime.day)])
    output_filename = 'live_scores_{0}.csv'.format(today_date)
    headers = ['League', 'Home Team Name', 'Home Team Goals', 'Away Team Goals', 'Away Team Name']
    with open(output_filename, 'w') as csv_file:
         writer = csv.writer(csv_file)
         writer.writerow(headers)
         for game in live_scores['games']:
            writer.writerow([game['league'], game['homeTeamName'],
                             game['goalsHomeTeam'], game['goalsAwayTeam'],
                             game['awayTeamName']])

def json_live_scores(live_scores):
    """Store output of live scores to a JSON file"""
    today_datetime = datetime.datetime.now()
    today_date = '_'.join([str(today_datetime.year), str(today_datetime.month),
                           str(today_datetime.day)])
    output_filename = 'live_scores_{0}.json'.format(today_date)
    with open(output_filename, 'w') as json_file:
        json.dump(live_scores['games'], json_file)

def get_team_scores(team, time, output):
    """ Queries the API and gets the particular team scores """
    team_id = TEAM_NAMES.get(team, None)
    if team_id:
        req = requests.get('{base_url}teams/{team_id}/fixtures?timeFrame=p{time}'.format(
            base_url=BASE_URL, team_id=team_id, time=time), headers=headers)
        if req.status_code == requests.codes.ok:
            team_scores = req.json()
            if len(team_scores["fixtures"]) == 0:
                click.secho("No action during past week. Change the time "
                            "parameter to get more fixtures.", fg="red", bold=True)
            else:
                globals()[output + '_team_scores'](team_scores, time)
        else:
            click.secho("No data for the team. Please check the team code.",
                fg="red", bold=True)
    else:
        click.secho("No data for the team. Please check the team code.",
            fg="red", bold=True)


def stdout_team_scores(team_scores, time):
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

def csv_team_scores(team_scores, time):
    """Store output of team scores to a CSV file"""
    output_filename = 'team_scores_{0}.csv'.format(time)
    headers = ['Date', 'Home Team Name', 'Home Team Goals', 'Away Team Goals',
               'Away Team Name']
    with open(output_filename, 'w') as csv_file:
         writer = csv.writer(csv_file)
         writer.writerow(headers)
         for score in team_scores['fixtures']:
            if score['status'] == 'FINISHED':
                writer.writerow([score["date"].split('T')[0], score['homeTeamName'],
                                 score['result']['goalsHomeTeam'],
                                 score['result']['goalsAwayTeam'],
                                 score['awayTeamName']])

def json_team_scores(team_scores, time):
    """Store output of team scores to a JSON file"""
    output_filename = 'team_scores_{0}.json'.format(time)
    data = []
    for score in team_scores['fixtures']:
        if score['status'] == 'FINISHED':
            item = {'date': score["date"].split('T')[0], 
                    'homeTeamName' : score['homeTeamName'],
                    'goalsHomeTeam' : score['result']['goalsHomeTeam'],
                    'goalsAwayTeam' : score['result']['goalsAwayTeam'],
                    'awayTeamName' : score['awayTeamName']}
            data.append(item)
    with open(output_filename, 'w') as json_file:
        json.dump({'team_scores' : data}, json_file)

def get_standings(league, output):
    """ Queries the API and gets the standings for a particular league """
    if not league:
        click.secho("Please specify a league. Example --standings --league=EPL",
            fg="red", bold=True)
        return
    league_id = LEAGUE_IDS[league]
    req = requests.get('{base_url}soccerseasons/{id}/leagueTable'.format(
            base_url=BASE_URL, id=league_id), headers=headers)
    if req.status_code == requests.codes.ok:
        globals()[output + '_standings'](req.json(), league)
    else:
        click.secho("No standings availble for {league}.".format(league=league),
            fg="red", bold=True)

def stdout_standings(league_table, league):
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

def csv_standings(league_table, league):
    """Store output of league standings to a CSV file"""
    output_filename = '{0}_standings.csv'.format(league)
    headers = ['Position', 'Team Name', 'Games Played', 'Goal For',
               'Goals Against', 'Goal Difference', 'Points']
    with open(output_filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for team in league_table['standing']:
            writer.writerow([team['position'], team['teamName'],
                             team['playedGames'], team['goals'],
                             team['goalsAgainst'], team['goalDifference'],
                             team['points']])

def json_standings(league_table, league):
    """Store output of league standings to a JSON file"""
    output_filename = '{0}_standings.json'.format(league)
    data = []
    for team in league_table['standing']:
        item = {'position' : team['position'], 'teamName' : team['teamName'],
                'playedGames' : team['playedGames'], 'goalsFor' : team['goals'],
                'goalsAgainst' : team['goalsAgainst'], 'goalDifference' : team['goalDifference'],
                'points' : team['points']}
        data.append(item)
    with open(output_filename, 'w') as json_file:
        json.dump({'standings' : data}, json_file)

def get_league_scores(league, time, output):
    """Queries the API and fetches the scores for fixtures
    based upon the league and time parameter"""
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
                globals()[output + '_league_scores'](fixtures_results, time)
        else:
            click.secho("No data for the given league",
                fg="red", bold=True)
        return

    req = requests.get('{base_url}fixtures?timeFrame=p{time}'.format(
        base_url=BASE_URL, time=str(time)), headers=headers)
    if req.status_code == requests.codes.ok:
            fixtures_results = req.json()
            globals()[output + '_league_scores'](fixtures_results, time)


def supported_leagues(total_data, stdout=True):
    """Filters out scores of unsupported leagues"""
    supported_leagues = {val: key for key, val in LEAGUE_IDS.items()}
    get_league_id = lambda x: int(x["_links"]["soccerseason"]["href"].split("/")[-1])
    fixtures = (fixture for fixture in total_data["fixtures"]
                if get_league_id(fixture) in supported_leagues)
    # Sort the scores by league to make it easier to read
    fixtures = sorted(fixtures, key=get_league_id)
    for league, scores in groupby(fixtures, key=get_league_id):
        league_name = " {0} ".format(supported_leagues[league])
        if stdout:
            # Print league header
            click.echo()
            click.secho("{:=^56}".format(league_name), fg="green")
            click.echo()
        for score in scores:
            yield league_name.strip(), score


def stdout_league_scores(total_data, time):
    """Prints the data in a pretty format"""
    for _, data in supported_leagues(total_data):
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

def csv_league_scores(total_data, time):
    """Store output of fixtures based on league and time to a CSV file"""
    output_filename = 'league_scores_{0}.csv'.format(time)
    headers = ['League', 'Home Team Name', 'Home Team Goals', 'Away Team Goals',
               'Away Team Name']
    with open(output_filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for league, score in supported_leagues(total_data, stdout=False):
            print score
            writer.writerow([league, score['homeTeamName'],
                             score['result']['goalsHomeTeam'],
                             score['result']['goalsAwayTeam'],
                             score['awayTeamName']])

def json_league_scores(total_data, time):
    """Store output of fixtures based on league and time to a JSON file"""
    output_filename = 'league_scores_{0}.json'.format(time)
    data = []
    for league, score in supported_leagues(total_data, stdout=False):
        item = {'league': league, 'homeTeamName' : score['homeTeamName'],
                'goalsHomeTeam' : score['result']['goalsHomeTeam'],
                'goalsAwayTeam' : score['result']['goalsAwayTeam'],
                'awayTeamName' : score['awayTeamName']}
        data.append(item)
    with open(output_filename, 'w') as json_file:
        json.dump({'league_scores' : data, 'time' : time}, json_file)

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
@click.option('-o', '--output', type=click.Choice(['stdout', 'csv', 'json']), default='stdout',
    help='Print output in stdout, CSV or JSON format')
def main(league, time, standings, team, live, output):
    """ A CLI for live and past football scores from various football leagues """
    if live:
        get_live_scores(output)
        return

    if standings:
        get_standings(league, output)
        return

    if team:
        get_team_scores(team, time, output)
        return

    get_league_scores(league, time, output)

if __name__ == '__main__':
    main()
