import click
import os
import requests
import sys

from soccer import leagueids, teamnames
from soccer.exceptions import IncorrectParametersException, APIErrorException
from soccer.writers import get_writer


BASE_URL = 'http://api.football-data.org/alpha/'
LIVE_URL = 'http://soccer-cli.appspot.com/'
LEAGUE_IDS = leagueids.LEAGUE_IDS
TEAM_NAMES = teamnames.team_names

try:
    api_token = os.environ['SOCCER_CLI_API_TOKEN']
except KeyError:
    from soccer.config import config
    api_token = config.get('SOCCER_CLI_API_TOKEN')

if not api_token:
    print ('No API Token detected. Please visit {0} and get an API Token, '
           'which will be used by the Soccer CLI to get access to the data'
           .format(BASE_URL))
    sys.exit(1)

headers = {
    'X-Auth-Token': api_token
}


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


@click.command()
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
def main(league, time, standings, team, live, use12hour, players, output_format, output_file, upcoming):
    """A CLI for live and past football scores from various football leagues"""
    try:
        if output_format == 'stdout' and output_file:
            raise IncorrectParametersException('Printing output to stdout and '
                                               'saving to a file are mutually exclusive')
        writer = get_writer(output_format, output_file)

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
