import click
import csv
import datetime
import json
import io

import leagueids
import leagueproperties

from abc import ABCMeta, abstractmethod
from itertools import groupby

LEAGUE_PROPERTIES = leagueproperties.LEAGUE_PROPERTIES
LEAGUE_IDS = leagueids.LEAGUE_IDS


def get_writer(output_format='stdout',output_file=None):
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
    def live_scores(self, live_scores):
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

    def team_scores(self, team_scores, time):
        """Prints the teams scores in a pretty format"""
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

    def standings(self, league_table, league):
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
                             str(team["playedGames"]), team["goalDifference"], str(team["points"])),
                            bold=True, fg="green")
            elif LEAGUE_PROPERTIES[league]["el"][0] <= team["position"] <= LEAGUE_PROPERTIES[league]["el"][1]:
                click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
                            (str(team["position"]), team["teamName"],
                             str(team["playedGames"]), team["goalDifference"], str(team["points"])),
                            fg="yellow")
            elif LEAGUE_PROPERTIES[league]["rl"][0] <= team["position"] <= LEAGUE_PROPERTIES[league]["rl"][1]:  # 5-15 in BL, 5-17 in others
                click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
                            (str(team["position"]), team["teamName"],
                             str(team["playedGames"]), team["goalDifference"], str(team["points"])),
                            fg="red")
            else:
                click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
                            (str(team["position"]), team["teamName"],
                             str(team["playedGames"]), team["goalDifference"], str(team["points"])),
                            fg="blue")

    def league_scores(self, total_data, time):
        """Prints the data in a pretty format"""
        seen = set()
        for league, data in self.supported_leagues(total_data):
            if league not in seen:
                seen.add(league) 
                league_name = " {0} ".format(league)
                click.secho("{:=^56}".format(league_name), fg="green")
                click.echo()
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
        today_date = '_'.join([str(today_datetime.year), str(today_datetime.month),
                               str(today_datetime.day)])
        headers = ['League', 'Home Team Name', 'Home Team Goals', 'Away Team Goals', 'Away Team Name']
        result = [headers]
        result.extend([game['league'], game['homeTeamName'], game['goalsHomeTeam'],
                       game['goalsAwayTeam'], game['awayTeamName']]
                      for game in live_scores['games'])
        self.generate_output(result)

    def team_scores(self, team_scores, time):
        """Store output of team scores to a CSV file"""
        headers = ['Date', 'Home Team Name', 'Home Team Goals', 'Away Team Goals',
                   'Away Team Name']
        result =[headers]
        result.extend([score["date"].split('T')[0], score['homeTeamName'],
                       score['result']['goalsHomeTeam'],
                       score['result']['goalsAwayTeam'],score['awayTeamName']]
                      for score in team_scores['fixtures']
                      if score['status'] == 'FINISHED')
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
        headers = ['League', 'Home Team Name', 'Home Team Goals', 'Away Team Goals',
                   'Away Team Name']
        result = [headers]
        result.extend([league, score['homeTeamName'],
                       score['result']['goalsHomeTeam'],
                       score['result']['goalsAwayTeam'], score['awayTeamName']] 
                      for league, score in self.supported_leagues(total_data))
        self.generate_output(result)

class Json(BaseWriter):

    def generate_output(self, result):
        if not self.output_filename:
            click.echo(json.dumps(result, indent=4, separators=(',', ': '), ensure_ascii=False))
        else:
            with io.open(self.output_filename, 'w', encoding='utf-8') as json_file:
                data = json.dumps(result, json_file, indent=4, separators=(',', ': '), ensure_ascii=False)
                json_file.write(data)

    def live_scores(self, live_scores):
        """Store output of live scores to a JSON file"""
        today_datetime = datetime.datetime.now()
        today_date = '_'.join([str(today_datetime.year), str(today_datetime.month),
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
            item = {'position': team['position'], 'teamName': team['teamName'],
                    'playedGames': team['playedGames'], 'goalsFor': team['goals'],
                    'goalsAgainst': team['goalsAgainst'], 'goalDifference': team['goalDifference'],
                    'points': team['points']}
            data.append(item)
        self.generate_output({'standings': data})

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