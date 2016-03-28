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

    def supported_leagues(self, total_data):
        """Filters out scores of unsupported leagues"""
        supported_leagues = {val: key for key, val in LEAGUE_IDS.items()}
        get_league_id = lambda x: int(x["_links"]["soccerseason"]["href"].split("/")[-1])
        fixtures = (fixture for fixture in total_data["fixtures"]
                    if get_league_id(fixture) in supported_leagues)

        # Sort the scores by league to make it easier to read
        fixtures = sorted(fixtures, key=get_league_id)
        for league, scores in groupby(fixtures, key=get_league_id):
            league = supported_leagues[league]
            for score in scores:
                yield league, score


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

    def live_scores(self, live_scores, use_12_hour_format):
        """Prints the live scores in a pretty format"""
        scores = sorted(live_scores["games"], key=lambda x: x["league"])
        for league, games in groupby(scores, key=lambda x: x["league"]):
            self.league_header(league)
            for game in games:
                self.scores(self.parse_result(game), add_new_line=False)
                click.secho('   %s' % Stdout.convert_utc_to_local_time(game["time"], use_12_hour_format),
                            fg=self.colors.TIME)
                click.echo()

    def team_scores(self, team_scores, time, show_datetime, use_12_hour_format):
        """Prints the teams scores in a pretty format"""
        for score in team_scores["fixtures"]:
            if score["status"] == "FINISHED":
                click.echo()
                click.secho("%s\t" % score["date"].split('T')[0],
                            fg=self.colors.TIME, nl=False)
                self.scores(self.parse_result(score))
            elif show_datetime:
                click.echo()
                self.scores(self.parse_result(score), add_new_line=False)
                click.secho('   %s' % Stdout.convert_utc_to_local_time(score["date"], 
                                        use_12_hour_format, show_datetime),
                                fg=self.colors.TIME)
                

    def team_players(self, team):
        """Prints the team players in a pretty format"""
        players = sorted(team['players'], key=lambda d: (d['jerseyNumber']))
        click.secho("%-4s %-25s    %-20s    %-20s    %-15s    %-10s" %
                    ("N.",  "NAME", "POSITION", "NATIONALITY", "BIRTHDAY",
                     "MARKET VALUE"), bold=True, fg=self.colors.MISC)
        for player in players:
            click.echo()
            click.secho("%-4s %-25s    %-20s    %-20s    %-15s    %-10s" % (
                        player["jerseyNumber"],
                        player["name"],
                        player["position"],
                        player["nationality"],
                        player["dateOfBirth"],
                        player["marketValue"]),
                        bold=True
                        )

    def standings(self, league_table, league):
        """ Prints the league standings in a pretty way """
        click.secho("%-6s  %-30s    %-10s    %-10s    %-10s" %
                    ("POS", "CLUB", "PLAYED", "GOAL DIFF", "POINTS"))
        positionlist = [team["position"] for team in league_table["standing"]]
        for team in league_table["standing"]:
            if team["goalDifference"] >= 0:
                team["goalDifference"] = ' ' + str(team["goalDifference"])

            # Define the upper and lower bounds for Champions League,
            # Europa League and Relegation places.
            # This is so we can highlight them appropriately.
            cl_upper = LEAGUE_PROPERTIES[league]['cl'][0]
            cl_lower = LEAGUE_PROPERTIES[league]['cl'][1]
            el_upper = LEAGUE_PROPERTIES[league]['el'][0]
            el_lower = LEAGUE_PROPERTIES[league]['el'][1]
            rl_upper = LEAGUE_PROPERTIES[league]['rl'][0]
            rl_lower = LEAGUE_PROPERTIES[league]['rl'][1]

            if cl_upper <= team["position"] <= cl_lower:
                click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" % (
                            team["position"],
                            team["teamName"],
                            team["playedGames"],
                            team["goalDifference"],
                            team["points"]
                            ),
                            bold=True, fg=self.colors.CL_POSITION)
            elif el_upper <= team["position"] <= el_lower:
                click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" % (
                            team["position"],
                            team["teamName"],
                            team["playedGames"],
                            team["goalDifference"],
                            team["points"]
                            ),
                            fg=self.colors.EL_POSITION)
            elif rl_upper <= team["position"] <= rl_lower:
                click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" % (
                            team["position"],
                            team["teamName"],
                            team["playedGames"],
                            team["goalDifference"],
                            team["points"]
                            ),
                            fg=self.colors.RL_POSITION)
            else:
                click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" % (
                           team["position"],
                           team["teamName"],
                           team["playedGames"],
                           team["goalDifference"],
                           team["points"]
                           ),
                           fg=self.colors.POSITION)

    def league_scores(self, total_data, time, show_datetime, use_12_hour_format):
        """Prints the data in a pretty format"""
        seen = set()
        for league, data in self.supported_leagues(total_data):
            if league not in seen:
                seen.add(league)
                self.league_header(league)
            self.scores(self.parse_result(data), add_new_line=not show_datetime)
            if show_datetime:
                click.secho('   %s' % Stdout.convert_utc_to_local_time(data["date"], 
                                        use_12_hour_format, show_datetime),
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
            return "-" if score == -1 else score

        if "result" in data:
            result = self.Result(
                data["homeTeamName"],
                valid_score(data["result"]["goalsHomeTeam"]),
                data["awayTeamName"],
                valid_score(data["result"]["goalsAwayTeam"]))
        else:
            result = self.Result(
                data["homeTeamName"],
                valid_score(data["goalsHomeTeam"]),
                data["awayTeamName"],
                valid_score(data["goalsAwayTeam"]))

        return result

    @staticmethod
    def convert_utc_to_local_time(time_str, use_12_hour_format, show_datetime=False):
        """Converts the API UTC time string to the local user time."""
        if not (time_str.endswith(" UTC") or time_str.endswith("Z")):
           return time_str

        today_utc = datetime.datetime.utcnow()
        utc_local_diff = today_utc - datetime.datetime.now()
        
        if time_str.endswith(" UTC"):
            time_str, _ = time_str.split(" UTC")
            utc_time = datetime.datetime.strptime(time_str, '%I:%M %p')
            utc_datetime = datetime.datetime(today_utc.year, today_utc.month, today_utc.day,
                                             utc_time.hour, utc_time.minute)
        else:
            utc_datetime = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
            
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
        today_datetime = datetime.datetime.now()
        today_date = '_'.join([str(today_datetime.year),
                               str(today_datetime.month),
                               str(today_datetime.day)])
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
        result.extend([score["date"].split('T')[0], score['homeTeamName'],
                       score['result']['goalsHomeTeam'],
                       score['result']['goalsAwayTeam'], score['awayTeamName']]
                      for score in team_scores['fixtures']
                      if score['status'] == 'FINISHED')
        self.generate_output(result)

    def team_players(self, team):
        """Store output of team players to a CSV file"""
        headers = ['Jersey Number', 'Name', 'Position', 'Nationality',
                   'Date of Birth', 'Market Value']
        result = [headers]

        result.extend([player['jerseyNumber'], player['name'],
                       player['position'], player['nationality'],
                       player['dateOfBirth'], player['marketValue']]
                      for player in team['players'])
        self.generate_output(result)

    def standings(self, league_table, league):
        """Store output of league standings to a CSV file"""
        headers = ['Position', 'Team Name', 'Games Played', 'Goal For',
                   'Goals Against', 'Goal Difference', 'Points']
        result = [headers]
        result.extend([team['position'], team['teamName'], team['playedGames'],
                       team['goals'], team['goalsAgainst'],
                       team['goalDifference'], team['points']]
                      for team in league_table['standing'])
        self.generate_output(result)

    def league_scores(self, total_data, time):
        """Store output of fixtures based on league and time to a CSV file"""
        headers = ['League', 'Home Team Name', 'Home Team Goals',
                   'Away Team Goals', 'Away Team Name']
        result = [headers]
        result.extend([league, score['homeTeamName'],
                       score['result']['goalsHomeTeam'],
                       score['result']['goalsAwayTeam'], score['awayTeamName']]
                      for league, score in self.supported_leagues(total_data))
        self.generate_output(result)


class Json(BaseWriter):

    def generate_output(self, result):
        if not self.output_filename:
            click.echo(json.dumps(result, indent=4, separators=(',', ': '),
                       ensure_ascii=False))
        else:
            with io.open(self.output_filename, 'w', encoding='utf-8') as json_file:
                data = json.dumps(result, json_file, indent=4,
                                  separators=(',', ': '), ensure_ascii=False)
                json_file.write(data)

    def live_scores(self, live_scores):
        """Store output of live scores to a JSON file"""
        today_datetime = datetime.datetime.now()
        today_date = '_'.join([str(today_datetime.year),
                              str(today_datetime.month),
                              str(today_datetime.day)])
        self.generate_output(live_scores['games'])

    def team_scores(self, team_scores, time):
        """Store output of team scores to a JSON file"""
        data = []
        for score in team_scores['fixtures']:
            if score['status'] == 'FINISHED':
                item = {'date': score["date"].split('T')[0],
                        'homeTeamName': score['homeTeamName'],
                        'goalsHomeTeam': score['result']['goalsHomeTeam'],
                        'goalsAwayTeam': score['result']['goalsAwayTeam'],
                        'awayTeamName': score['awayTeamName']}
                data.append(item)
        self.generate_output({'team_scores': data})

    def standings(self, league_table, league):
        """Store output of league standings to a JSON file"""
        data = []
        for team in league_table['standing']:
            item = {'position': team['position'],
                    'teamName': team['teamName'],
                    'playedGames': team['playedGames'],
                    'goalsFor': team['goals'],
                    'goalsAgainst': team['goalsAgainst'],
                    'goalDifference': team['goalDifference'],
                    'points': team['points']}
            data.append(item)
        self.generate_output({'standings': data})

    def team_players(self, team):
        """Store output of team players to a JSON file"""
        data = []
        for player in team['players']:
            item = {'jerseyNumber': player['jerseyNumber'],
                    'name': player['name'],
                    'position': player['position'],
                    'nationality': player['nationality'],
                    'dateOfBirth': player['dateOfBirth'],
                    'marketValue': player['marketValue']}
            data.append(item)
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
