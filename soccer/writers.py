import click
import csv
import datetime
import json
import io

from abc import ABCMeta, abstractmethod
from itertools import groupby
from collections import namedtuple

from soccer import leagueids, leagueproperties

LEAGUE_PROPERTIES = leagueproperties.LEAGUE_PROPERTIES
LEAGUE_IDS = leagueids.LEAGUE_IDS


def get_writer(output_format='stdout', output_file=None):
    return globals()[output_format.capitalize()](output_file)


class BaseWriter(object):

    __metaclass__ = ABCMeta

    def __init__(self, output_file):
        self.output_filename = output_file

    @abstractmethod
    def live_scores(self, live_scores):
        pass

    @abstractmethod
    def team_scores(self, team_scores, time):
        pass

    @abstractmethod
    def team_players(self, team):
        pass

    @abstractmethod
    def standings(self, league_table, league):
        pass

    @abstractmethod
    def league_scores(self, total_data, time):
        pass


class Stdout(BaseWriter):

    def __init__(self, output_file):
        self.Result = namedtuple("Result", "homeTeam, goalsHomeTeam, awayTeam, goalsAwayTeam")

        enums = dict(
            WIN="red",
            LOSE="blue",
            TIE="yellow",
            MISC="green",
            TIME="yellow",
            CL_POSITION="green",
            EL_POSITION="yellow",
            RL_POSITION="red",
            POSITION="blue"
        )
        self.colors = type('Enum', (), enums)

    def live_scores(self, live_scores):
        """Prints the live scores in a pretty format"""
        scores = sorted(live_scores, key=lambda x: x["league"])
        for league, games in groupby(scores, key=lambda x: x["league"]):
            self.league_header(league)
            for game in games:
                self.scores(self.parse_result(game), add_new_line=False)
                click.secho('   %s' % Stdout.utc_to_local(game["time"],
                                                          use_12_hour_format=False),
                            fg=self.colors.TIME)
                click.echo()

    def team_scores(self, team_scores, time, show_datetime, use_12_hour_format):
        """Prints the teams scores in a pretty format"""
        for score in team_scores["matches"]:
            if score["status"] == "FINISHED":
                click.secho("%s\t" % score["utcDate"].split('T')[0],
                            fg=self.colors.TIME, nl=False)
                self.scores(self.parse_result(score))
            elif show_datetime:
                self.scores(self.parse_result(score), add_new_line=False)
                click.secho('   %s' % Stdout.utc_to_local(score["utcDate"],
                                                          use_12_hour_format,
                                                          show_datetime),
                            fg=self.colors.TIME)

    def team_players(self, team):
        """Prints the team players in a pretty format"""
        players = sorted(team, key=lambda d: d['shirtNumber'])
        click.secho("%-4s %-25s    %-20s    %-20s    %-15s" %
                    ("N.",  "NAME", "POSITION", "NATIONALITY", "BIRTHDAY"),
                    bold=True,
                    fg=self.colors.MISC)
        fmt = (u"{shirtNumber:<4} {name:<28} {position:<23} {nationality:<23}"
               u" {dateOfBirth:<18}")
        for player in players:
            click.secho(fmt.format(**player), bold=True)

    def standings(self, league_table, league):
        """ Prints the league standings in a pretty way """
        click.secho("%-6s  %-30s    %-10s    %-10s    %-10s" %
                    ("POS", "CLUB", "PLAYED", "GOAL DIFF", "POINTS"))
        for team in league_table["standings"][0]["table"]:
            if team["goalDifference"] >= 0:
                team["goalDifference"] = ' ' + str(team["goalDifference"])

            # Define the upper and lower bounds for Champions League,
            # Europa League and Relegation places.
            # This is so we can highlight them appropriately.
            cl_upper, cl_lower = LEAGUE_PROPERTIES[league]['cl']
            el_upper, el_lower = LEAGUE_PROPERTIES[league]['el']
            rl_upper, rl_lower = LEAGUE_PROPERTIES[league]['rl']
            team['teamName'] = team['team']['name']
            team_str = (u"{position:<7} {teamName:<33} {playedGames:<12}"
                        u" {goalDifference:<14} {points}").format(**team)
            if cl_upper <= team["position"] <= cl_lower:
                click.secho(team_str, bold=True, fg=self.colors.CL_POSITION)
            elif el_upper <= team["position"] <= el_lower:
                click.secho(team_str, fg=self.colors.EL_POSITION)
            elif rl_upper <= team["position"] <= rl_lower:
                click.secho(team_str, fg=self.colors.RL_POSITION)
            else:
                click.secho(team_str, fg=self.colors.POSITION)

    def league_scores(self, total_data, time, show_datetime,
                      use_12_hour_format):
        """Prints the data in a pretty format"""
        for match in total_data['matches']:
            self.scores(self.parse_result(match), add_new_line=not show_datetime)
            if show_datetime:
                click.secho('   %s' % Stdout.utc_to_local(data["date"],
                                                          use_12_hour_format,
                                                          show_datetime),
                            fg=self.colors.TIME)
            click.echo()

    def league_header(self, league):
        """Prints the league header"""
        league_name = " {0} ".format(league)
        click.secho("{:=^62}".format(league_name), fg=self.colors.MISC)
        click.echo()

    def scores(self, result, add_new_line=True):
        """Prints out the scores in a pretty format"""
        if result.goalsHomeTeam > result.goalsAwayTeam:
            homeColor, awayColor = (self.colors.WIN, self.colors.LOSE)
        elif result.goalsHomeTeam < result.goalsAwayTeam:
            homeColor, awayColor = (self.colors.LOSE, self.colors.WIN)
        else:
            homeColor = awayColor = self.colors.TIE

        click.secho('%-25s %2s' % (result.homeTeam, result.goalsHomeTeam),
                    fg=homeColor, nl=False)
        click.secho("  vs ", nl=False)
        click.secho('%2s %s' % (result.goalsAwayTeam,
                                result.awayTeam.rjust(25)), fg=awayColor,
                    nl=add_new_line)

    def parse_result(self, data):
        """Parses the results and returns a Result namedtuple"""
        def valid_score(score):
            return "" if score == None else score

        return self.Result(
            data["homeTeam"]["name"],
            valid_score(data["score"]["fullTime"]["homeTeam"]),
            data["awayTeam"]["name"],
            valid_score(data["score"]["fullTime"]["awayTeam"]))

    @staticmethod
    def utc_to_local(time_str, use_12_hour_format, show_datetime=False):
        """Converts the API UTC time string to the local user time."""
        if not (time_str.endswith(" UTC") or time_str.endswith("Z")):
            return time_str

        today_utc = datetime.datetime.utcnow()
        utc_local_diff = today_utc - datetime.datetime.now()

        if time_str.endswith(" UTC"):
            time_str, _ = time_str.split(" UTC")
            utc_time = datetime.datetime.strptime(time_str, '%I:%M %p')
            utc_datetime = datetime.datetime(today_utc.year,
                                             today_utc.month,
                                             today_utc.day,
                                             utc_time.hour,
                                             utc_time.minute)
        else:
            utc_datetime = datetime.datetime.strptime(time_str,
                                                      '%Y-%m-%dT%H:%M:%SZ')

        local_time = utc_datetime - utc_local_diff

        if use_12_hour_format:
            date_format = '%I:%M %p' if not show_datetime else '%a %d, %I:%M %p'
        else:
            date_format = '%H:%M' if not show_datetime else '%a %d, %H:%M'

        return datetime.datetime.strftime(local_time, date_format)


class Csv(BaseWriter):

    def generate_output(self, result):
        if not self.output_filename:
            for row in result:
                click.echo(u','.join(unicode(item) for item in row))
        else:
            with open(self.output_filename, 'w') as csv_file:
                writer = csv.writer(csv_file)
                for row in result:
                    row = [unicode(s).encode('utf-8') for s in row]
                    writer.writerow(row)

    def live_scores(self, live_scores):
        """Store output of live scores to a CSV file"""
        headers = ['League', 'Home Team Name', 'Home Team Goals',
                   'Away Team Goals', 'Away Team Name']
        result = [headers]
        result.extend([game['league'], game['homeTeamName'],
                       game['goalsHomeTeam'], game['goalsAwayTeam'],
                       game['awayTeamName']] for game in live_scores['games'])
        self.generate_output(result)

    def team_scores(self, team_scores, time):
        """Store output of team scores to a CSV file"""
        headers = ['Date', 'Home Team Name', 'Home Team Goals',
                   'Away Team Goals', 'Away Team Name']
        result = [headers]
        result.extend([score["utcDate"].split('T')[0],
                       score['homeTeam']['name'],
                       score['score']['fullTime']['homeTeam'],
                       score['score']['fullTime']['awayTeam'],
                       score['awayTeam']['name']]
                      for score in team_scores['matches']
                      if score['status'] == 'FINISHED')
        self.generate_output(result)

    def team_players(self, team):
        """Store output of team players to a CSV file"""
        headers = ['Jersey Number', 'Name', 'Position', 'Nationality',
                   'Date of Birth']
        result = [headers]

        result.extend([player['shirtNumber'],
                       player['name'],
                       player['position'],
                       player['nationality'],
                       player['dateOfBirth']]
                      for player in team)
        self.generate_output(result)

    def standings(self, league_table, league):
        """Store output of league standings to a CSV file"""
        headers = ['Position', 'Team Name', 'Games Played', 'Goal For',
                   'Goals Against', 'Goal Difference', 'Points']
        result = [headers]
        result.extend([team['position'],
                       team['team']['name'],
                       team['playedGames'],
                       team['goalsFor'],
                       team['goalsAgainst'],
                       team['goalDifference'],
                       team['points']]
                       for team in league_table['standings'][0]['table'])
        self.generate_output(result)

    def league_scores(self, total_data, time, show_upcoming, use_12_hour_format):
        """Store output of fixtures based on league and time to a CSV file"""
        headers = ['League', 'Home Team Name', 'Home Team Goals',
                   'Away Team Goals', 'Away Team Name']
        result = [headers]
        league = total_data['competition']['name']
        result.extend([league,
                       score['homeTeam']['name'],
                       score['score']['fullTime']['homeTeam'],
                       score['score']['fullTime']['awayTeam'],
                        score['awayTeam']['name']]
                       for score in total_data['matches'])
        self.generate_output(result)


class Json(BaseWriter):

    def generate_output(self, result):
        if not self.output_filename:
            click.echo(json.dumps(result,
                                  indent=4,
                                  separators=(',', ': '),
                                  ensure_ascii=False))
        else:
            with io.open(self.output_filename, 'w', encoding='utf-8') as f:
                data = json.dumps(result, f, indent=4,
                                  separators=(',', ': '), ensure_ascii=False)
                f.write(data)

    def live_scores(self, live_scores):
        """Store output of live scores to a JSON file"""
        self.generate_output(live_scores['games'])

    def team_scores(self, team_scores, time):
        """Store output of team scores to a JSON file"""
        data = []
        for score in team_scores['matches']:
            if score['status'] == 'FINISHED':
                item = {'date': score["utcDate"].split('T')[0],
                        'homeTeamName': score['homeTeam']['name'],
                        'goalsHomeTeam': score['score']['fullTime']['homeTeam'],
                        'goalsAwayTeam': score['score']['fullTime']['awayTeam'],
                        'awayTeamName': score['awayTeam']['name']}
                data.append(item)
        self.generate_output({'team_scores': data})

    def standings(self, league_table, league):
        """Store output of league standings to a JSON file"""
        data = []
        for team in league_table['standings'][0]['table']:
            item = {'position': team['position'],
                    'teamName': team['team'],
                    'playedGames': team['playedGames'],
                    'goalsFor': team['goalsFor'],
                    'goalsAgainst': team['goalsAgainst'],
                    'goalDifference': team['goalDifference'],
                    'points': team['points']}
            data.append(item)
        self.generate_output({'standings': data})

    def team_players(self, team):
        """Store output of team players to a JSON file"""
        keys = 'shirtNumber name position nationality dateOfBirth'.split()
        data = [{key: player[key] for key in keys} for player in team]
        self.generate_output({'players': data})

    def league_scores(self, total_data, time):
        """Store output of fixtures based on league and time to a JSON file"""
        data = []
        for league, score in self.supported_leagues(total_data):
            item = {'league': league, 'homeTeamName': score['homeTeamName'],
                    'goalsHomeTeam': score['result']['goalsHomeTeam'],
                    'goalsAwayTeam': score['result']['goalsAwayTeam'],
                    'awayTeamName': score['awayTeamName']}
            data.append(item)
        self.generate_output({'league_scores': data, 'time': time})
