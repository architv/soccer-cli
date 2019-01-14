import os
import sys
import json

import click

from soccer import leagueids
from soccer.exceptions import IncorrectParametersException
from soccer.writers import get_writer
from soccer.request_handler import RequestHandler


def load_json(file):
    """Load JSON file at app start"""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, file)) as jfile:
        data = json.load(jfile)
    return data


LEAGUE_IDS = leagueids.LEAGUE_IDS
TEAM_DATA = load_json("teams.json")["teams"]
TEAM_NAMES = {team["code"]: team["id"] for team in TEAM_DATA}


def get_input_key():
    """Input API key and validate"""
    click.secho("No API key found!", fg="yellow", bold=True)
    click.secho("Please visit {} and get an API token.".format(RequestHandler.BASE_URL),
                fg="yellow",
                bold=True)
    while True:
        confkey = click.prompt(click.style("Enter API key",
                                           fg="yellow", bold=True))
        if len(confkey) == 32:  # 32 chars
            try:
                int(confkey, 16)  # hexadecimal
            except ValueError:
                click.secho("Invalid API key", fg="red", bold=True)
            else:
                break
        else:
            click.secho("Invalid API key", fg="red", bold=True)
    return confkey


def load_config_key():
    """Load API key from config file, write if needed"""
    global api_token
    try:
        api_token = os.environ['SOCCER_CLI_API_TOKEN']
    except KeyError:
        home = os.path.expanduser("~")
        config = os.path.join(home, ".soccer-cli.ini")
        if not os.path.exists(config):
            with open(config, "w") as cfile:
                key = get_input_key()
                cfile.write(key)
        else:
            with open(config, "r") as cfile:
                key = cfile.read()
        if key:
            api_token = key
        else:
            os.remove(config)  # remove 0-byte file
            click.secho('No API Token detected. '
                        'Please visit {0} and get an API Token, '
                        'which will be used by Soccer CLI '
                        'to get access to the data.'
                        .format(RequestHandler.BASE_URL), fg="red", bold=True)
            sys.exit(1)
    return api_token


def map_team_id(code):
    """Take in team ID, read JSON file to map ID to name"""
    for team in TEAM_DATA:
        if team["code"] == code:
            click.secho(team["name"], fg="green")
            break
    else:
        click.secho("No team found for this code", fg="red", bold=True)


def list_team_codes():
    """List team names in alphabetical order of team ID, per league."""
    # Sort teams by league, then alphabetical by code
    cleanlist = sorted(TEAM_DATA, key=lambda k: (k["league"]["name"], k["code"]))
    # Get league names
    leaguenames = sorted(list(set([team["league"]["name"] for team in cleanlist])))
    for league in leaguenames:
        teams = [team for team in cleanlist if team["league"]["name"] == league]
        click.secho(league, fg="green", bold=True)
        for team in teams:
            if team["code"] != "null":
                click.secho(u"{0}: {1}".format(team["code"], team["name"]), fg="yellow")
        click.secho("")


@click.command()
@click.option('--apikey', default=load_config_key,
              help="API key to use.")
@click.option('--list', 'listcodes', is_flag=True,
              help="List all valid team code/team name pairs.")
@click.option('--live', is_flag=True,
              help="Shows live scores from various leagues.")
@click.option('--use12hour', is_flag=True, default=False,
              help="Displays the time using 12 hour format instead of 24 (default).")
@click.option('--standings', '-s', is_flag=True,
              help="Standings for a particular league.")
@click.option('--league', '-l', type=click.Choice(LEAGUE_IDS.keys()),
              help=("Select fixtures from a particular league."))
@click.option('--players', is_flag=True,
              help="Shows players for a particular team.")
@click.option('--team', type=click.Choice(TEAM_NAMES.keys()),
              help=("Choose a particular team's fixtures."))
@click.option('--lookup', is_flag=True,
              help="Get full team name from team code when used with --team command.")
@click.option('--time', default=6,
              help=("The number of days in the past for which you "
                    "want to see the scores, or the number of days "
                    "in the future when used with --upcoming"))
@click.option('--upcoming', is_flag=True, default=False,
              help="Displays upcoming games when used with --time command.")
@click.option('--stdout', 'output_format', flag_value='stdout', default=True,
              help="Print to stdout.")
@click.option('--csv', 'output_format', flag_value='csv',
              help='Output in CSV format.')
@click.option('--json', 'output_format', flag_value='json',
              help='Output in JSON format.')
@click.option('-o', '--output-file', default=None,
              help="Save output to a file (only if csv or json option is provided).")
def main(league, time, standings, team, live, use12hour, players,
         output_format, output_file, upcoming, lookup, listcodes, apikey):
    """
    A CLI for live and past football scores from various football leagues.

    League codes:

    \b
    - CL: Champions League
    - PL: English Premier League
    - ELC: English Championship
    - EL1: English League One
    - FL1: French Ligue 1
    - FL2: French Ligue 2
    - BL: German Bundesliga
    - BL2: 2. Bundesliga
    - SA: Serie A
    - DED: Eredivisie
    - PPL: Primeira Liga
    - PD: Primera Division
    - SD: Segunda Division
    """
    headers = {'X-Auth-Token': apikey}

    try:
        if output_format == 'stdout' and output_file:
            raise IncorrectParametersException('Printing output to stdout and '
                                               'saving to a file are mutually exclusive')
        writer = get_writer(output_format, output_file)
        rh = RequestHandler(headers, LEAGUE_IDS, TEAM_NAMES, writer)

        if listcodes:
            list_team_codes()
            return

        if live:
            rh.get_live_scores(use12hour)
            return

        if standings:
            if not league:
                raise IncorrectParametersException('Please specify a league. '
                                                   'Example --standings --league=PL')
            if league == 'CL':
                raise IncorrectParametersException('Standings for CL - '
                                                   'Champions League not supported')
            rh.get_standings(league)
            return

        if team:
            if lookup:
                map_team_id(team)
                return
            if players:
                rh.get_team_players(team)
                return
            else:
                rh.get_team_scores(team, time, upcoming, use12hour)
                return

        rh.get_league_scores(league, time, upcoming, use12hour)
    except IncorrectParametersException as e:
        click.secho(str(e), fg="red", bold=True)


if __name__ == '__main__':
    main()
