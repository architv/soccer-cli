import click
import os
import requests
import sys
import json

from soccer import leagueids
from soccer.exceptions import IncorrectParametersException, APIErrorException
from soccer.writers import get_writer


BASE_URL = 'http://api.football-data.org/alpha/'
LIVE_URL = 'http://soccer-cli.appspot.com/'
LEAGUE_IDS = leagueids.LEAGUE_IDS


def load_json(file):
    """Load JSON file at app start"""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, file)) as jfile:
        data = json.load(jfile)
    return data


TEAM_DATA = load_json("teams.json")["teams"]
TEAM_NAMES = {team["code"]: team["id"] for team in TEAM_DATA}


def get_input_key():
    """Input API key and validate"""
    click.secho("No API key found!", fg="yellow", bold=True)
    click.secho("Please visit {0} and get an API token.".format(BASE_URL),
                fg="yellow", bold=True)
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
        config = os.path.join(home, "soccer-cli.ini")
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
                        .format(BASE_URL), fg="red", bold=True)
            sys.exit(1)
    return api_token


def _get(url):
    """Handles api.football-data.org requests"""
    req = requests.get(BASE_URL+url, headers=headers)

    if req.status_code == requests.codes.ok:
        return req

    if req.status_code == requests.codes.bad:
        raise APIErrorException('Invalid request. Check parameters.')

    if req.status_code == requests.codes.forbidden:
        raise APIErrorException('This resource is restricted')

    if req.status_code == requests.codes.not_found:
        raise APIErrorException('This resource does not exist. Check parameters')

    if req.status_codes == requests.codes.too_many_requests:
        raise APIErrorException('You have exceeded your allowed requests per minute/day')


def get_live_scores(writer, use_12_hour_format):
    """Gets the live scores"""
    req = requests.get(LIVE_URL)
    if req.status_code == requests.codes.ok:
        scores = req.json()
        if len(scores["games"]) == 0:
            click.secho("No live action currently", fg="red", bold=True)
            return
        writer.live_scores(scores, use_12_hour_format)
    else:
        click.secho("There was problem getting live scores", fg="red", bold=True)


def get_team_scores(team, time, writer, show_upcoming, use_12_hour_format):
    """Queries the API and gets the particular team scores"""
    team_id = TEAM_NAMES.get(team, None)
    time_frame = 'n' if show_upcoming else 'p'
    if team_id:
        try:
            req = _get('teams/{team_id}/fixtures?timeFrame={time_frame}{time}'.format(
                        team_id=team_id, time_frame=time_frame, time=time))
            team_scores = req.json()
            if len(team_scores["fixtures"]) == 0:
                click.secho("No action during past week. Change the time "
                            "parameter to get more fixtures.", fg="red", bold=True)
            else:
                writer.team_scores(team_scores, time, show_upcoming, use_12_hour_format)
        except APIErrorException as e:
            click.secho(e.args[0],
                        fg="red", bold=True)
    else:
        click.secho("Team code is not correct.",
                    fg="red", bold=True)


def get_standings(league, writer):
    """Queries the API and gets the standings for a particular league"""
    league_id = LEAGUE_IDS[league]
    try:
        req = _get('soccerseasons/{id}/leagueTable'.format(
                    id=league_id))
        writer.standings(req.json(), league)
    except APIErrorException:
        # Click handles incorrect League codes so this will only come up
        # if that league does not have standings available. ie. Champions League
        click.secho("No standings availble for {league}.".format(league=league),
                    fg="red", bold=True)


def get_league_scores(league, time, writer, show_upcoming, use_12_hour_format):

    """
    Queries the API and fetches the scores for fixtures
    based upon the league and time parameter
    """
    time_frame = 'n' if show_upcoming else 'p'
    if league:
        try:
            league_id = LEAGUE_IDS[league]
            req = _get('soccerseasons/{id}/fixtures?timeFrame={time_frame}{time}'.format(
                 id=league_id, time_frame=time_frame, time=str(time)))
            fixtures_results = req.json()
            # no fixtures in the past week. display a help message and return
            if len(fixtures_results["fixtures"]) == 0:
                click.secho("No {league} matches in the past week.".format(league=league),
                            fg="red", bold=True)
                return
            writer.league_scores(fixtures_results, time, show_upcoming, use_12_hour_format)
        except APIErrorException:
            click.secho("No data for the given league.", fg="red", bold=True)
    else:
        # When no league specified. Print all available in time frame.
        try:
            req = _get('fixtures?timeFrame={time_frame}{time}'.format(
                 time_frame=time_frame, time=str(time)))
            fixtures_results = req.json()
            writer.league_scores(fixtures_results, time, show_upcoming, use_12_hour_format)
        except APIErrorException:
            click.secho("No data available.", fg="red", bold=True)


def get_team_players(team, writer):
    """
    Queries the API and fetches the players
    for a particular team
    """
    team_id = TEAM_NAMES.get(team, None)
    try:
        req = _get('teams/{team_id}/players'.format(
                   team_id=team_id))
        team_players = req.json()
        if int(team_players["count"]) == 0:
            click.secho("No players found for this team", fg="red", bold=True)
        else:
            writer.team_players(team_players)
    except APIErrorException:
        click.secho("No data for the team. Please check the team code.",
                    fg="red", bold=True)


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
@click.option('--apikey', default=load_config_key, help="API key to use")
@click.option('--list', 'listcodes', is_flag=True, help="List all valid team code/team name pairs")
@click.option('--live', is_flag=True, help="Shows live scores from various leagues")
@click.option('--use12hour', is_flag=True, default=False, help="Displays the time using 12 hour format instead of 24 (default).")
@click.option('--standings', is_flag=True, help="Standings for a particular league")
@click.option('--league', '-league', type=click.Choice(LEAGUE_IDS.keys()),
              help=("Choose the league whose fixtures you want to see. "
                    "See league codes listed in README."))
@click.option('--players', is_flag=True, help="Shows players for a particular team")
@click.option('--team', type=click.Choice(TEAM_NAMES.keys()),
              help=("Choose the team whose fixtures you want to see. "
                    "See team codes listed in README."))
@click.option('--lookup', is_flag=True, help="Get team name from team code when used with --team command.")
@click.option('--time', default=6,
              help="The number of days in the past for which you want to see the scores")
@click.option('--upcoming', is_flag=True, default=False, help="Displays upcoming games when used with --time command.")
@click.option('--stdout', 'output_format', flag_value='stdout',
              default=True, help="Print to stdout")
@click.option('--csv', 'output_format', flag_value='csv',
              help='Output in CSV format')
@click.option('--json', 'output_format', flag_value='json',
              help='Output in JSON format')
@click.option('-o', '--output-file', default=None,
              help="Save output to a file (only if csv or json option is provided)")
def main(league, time, standings, team, live, use12hour, players, output_format, output_file, upcoming, lookup, listcodes, apikey):
    """A CLI for live and past football scores from various football leagues"""
    global headers
    headers = {
        'X-Auth-Token': apikey
    }
    try:
        if output_format == 'stdout' and output_file:
            raise IncorrectParametersException('Printing output to stdout and '
                                               'saving to a file are mutually exclusive')
        writer = get_writer(output_format, output_file)

        if listcodes:
            list_team_codes()
            return

        if live:
            get_live_scores(writer, use12hour)
            return

        if standings:
            if not league:
                raise IncorrectParametersException('Please specify a league. '
                                                   'Example --standings --league=EPL')
            get_standings(league, writer)
            return

        if team:
            if lookup:
                map_team_id(team)
                return
            if players:
                get_team_players(team, writer)
                return
            else:
                get_team_scores(team, time, writer, upcoming, use12hour)
                return

        get_league_scores(league, time, writer, upcoming, use12hour)
    except IncorrectParametersException as e:
        click.secho(e.message, fg="red", bold=True)

if __name__ == '__main__':
    main()
