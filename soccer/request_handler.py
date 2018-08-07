import requests
import click
from soccer.exceptions import APIErrorException


class RequestHandler(object):

    BASE_URL = 'http://api.football-data.org/v1/'
    LIVE_URL = 'http://soccer-cli.appspot.com/'

    def __init__(self, headers, league_ids, team_names, writer):
        self.headers = headers
        self.league_ids = league_ids
        self.team_names = team_names
        self.writer = writer

    def _get(self, url):
        """Handles api.football-data.org requests"""
        req = requests.get(RequestHandler.BASE_URL+url, headers=self.headers)

        if req.status_code == requests.codes.ok:
            return req

        if req.status_code == requests.codes.bad:
            raise APIErrorException('Invalid request. Check parameters.')

        if req.status_code == requests.codes.forbidden:
            raise APIErrorException('This resource is restricted')

        if req.status_code == requests.codes.not_found:
            raise APIErrorException('This resource does not exist. Check parameters')

        if req.status_code == requests.codes.too_many_requests:
            raise APIErrorException('You have exceeded your allowed requests per minute/day')

    def get_live_scores(self, use_12_hour_format):
        """Gets the live scores"""
        req = requests.get(RequestHandler.LIVE_URL)
        if req.status_code == requests.codes.ok:
            scores = req.json()
            if len(scores["games"]) == 0:
                click.secho("No live action currently", fg="red", bold=True)
                return
            self.writer.live_scores(scores, use_12_hour_format)
        else:
            click.secho("There was problem getting live scores", fg="red", bold=True)

    def get_team_scores(self, team, time, show_upcoming, use_12_hour_format):
        """Queries the API and gets the particular team scores"""
        team_id = self.team_names.get(team, None)
        time_frame = 'n' if show_upcoming else 'p'
        if team_id:
            try:
                req = self._get('teams/{team_id}/fixtures?timeFrame={time_frame}{time}'.format(
                            team_id=team_id, time_frame=time_frame, time=time))
                team_scores = req.json()
                if len(team_scores["fixtures"]) == 0:
                    click.secho("No action during past week. Change the time "
                                "parameter to get more fixtures.", fg="red", bold=True)
                else:
                    self.writer.team_scores(team_scores, time, show_upcoming, use_12_hour_format)
            except APIErrorException as e:
                click.secho(e.args[0],
                            fg="red", bold=True)
        else:
            click.secho("Team code is not correct.",
                        fg="red", bold=True)

    def get_standings(self, league):
        """Queries the API and gets the standings for a particular league"""
        league_id = self.league_ids[league]
        try:
            req = self._get('soccerseasons/{id}/leagueTable'.format(
                        id=league_id))
            self.writer.standings(req.json(), league)
        except APIErrorException:
            # Click handles incorrect League codes so this will only come up
            # if that league does not have standings available. ie. Champions League
            click.secho("No standings availble for {league}.".format(league=league),
                        fg="red", bold=True)

    def get_league_scores(self, league, time, show_upcoming, use_12_hour_format):

        """
        Queries the API and fetches the scores for fixtures
        based upon the league and time parameter
        """
        time_frame = 'n' if show_upcoming else 'p'
        if league:
            try:
                league_id = self.league_ids[league]
                req = self._get('soccerseasons/{id}/fixtures?timeFrame={time_frame}{time}'.format(
                     id=league_id, time_frame=time_frame, time=str(time)))
                fixtures_results = req.json()
                # no fixtures in the past week. display a help message and return
                if len(fixtures_results["fixtures"]) == 0:
                    click.secho("No {league} matches in the past week.".format(league=league),
                                fg="red", bold=True)
                    return
                self.writer.league_scores(fixtures_results,
                                          time, show_upcoming,
                                          use_12_hour_format)
            except APIErrorException:
                click.secho("No data for the given league.", fg="red", bold=True)
        else:
            # When no league specified. Print all available in time frame.
            try:
                req = self._get('fixtures?timeFrame={time_frame}{time}'.format(
                     time_frame=time_frame, time=str(time)))
                fixtures_results = req.json()
                self.writer.league_scores(fixtures_results,
                                          time,
                                          show_upcoming,
                                          use_12_hour_format)
            except APIErrorException:
                click.secho("No data available.", fg="red", bold=True)

    def get_team_players(self, team):
        """
        Queries the API and fetches the players
        for a particular team
        """
        team_id = self.team_names.get(team, None)
        try:
            req = self._get('teams/{team_id}/players'.format(
                       team_id=team_id))
            team_players = req.json()
            if int(team_players["count"]) == 0:
                click.secho("No players found for this team", fg="red", bold=True)
            else:
                self.writer.team_players(team_players)
        except APIErrorException:
            click.secho("No data for the team. Please check the team code.",
                        fg="red", bold=True)
