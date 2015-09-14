#!/usr/bin/env python

import click
import csv
import datetime
import json

import leagueids
import leagueproperties

from itertools import groupby

LEAGUE_PROPERTIES = leagueproperties.LEAGUE_PROPERTIES
LEAGUE_IDS = leagueids.LEAGUE_IDS


def get_writer(output):
    if output == 'stdout':
        return Console()
    elif output == 'json':
        return JSON()
    elif output == 'csv':
        return CSV()


def supported_leagues(total_data, writer):
    """Filters out scores of unsupported leagues"""
    supported_leagues = {val: key for key, val in LEAGUE_IDS.items()}
    get_league_id = lambda x: int(x["_links"]["soccerseason"]["href"].split("/")[-1])
    fixtures = (fixture for fixture in total_data["fixtures"]
                if get_league_id(fixture) in supported_leagues)

    # Sort the scores by league to make it easier to read
    fixtures = sorted(fixtures, key=get_league_id)
    for league, scores in groupby(fixtures, key=get_league_id):
        writer.league_header(supported_leagues[league])
        for score in scores:
            yield supported_leagues[league].strip(), score


class Console(object):
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
        for _, data in supported_leagues(total_data, self):
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

    def league_header(self, league_name):
        """Prints the league header"""
        click.echo()
        league_name = " {0} ".format(league_name)
        click.secho("{:=^56}".format(league_name), fg="green")
        click.echo()


class CSV(object):
    def live_scores(self, live_scores):
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

    def team_scores(self, team_scores, time):
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

    def standings(self, league_table, league):
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

    def league_scores(self, total_data, time):
        """Store output of fixtures based on league and time to a CSV file"""
        output_filename = 'league_scores_{0}.csv'.format(time)
        headers = ['League', 'Home Team Name', 'Home Team Goals', 'Away Team Goals',
                   'Away Team Name']
        with open(output_filename, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)
            for league, score in supported_leagues(total_data, self):
                print score
                writer.writerow([league, score['homeTeamName'],
                                 score['result']['goalsHomeTeam'],
                                 score['result']['goalsAwayTeam'],
                                 score['awayTeamName']])

    def league_header(self, league_name):
        pass


class JSON(object):
    def live_scores(self, live_scores):
        """Store output of live scores to a JSON file"""
        today_datetime = datetime.datetime.now()
        today_date = '_'.join([str(today_datetime.year), str(today_datetime.month),
                               str(today_datetime.day)])
        output_filename = 'live_scores_{0}.json'.format(today_date)
        with open(output_filename, 'w') as json_file:
            json.dump(live_scores['games'], json_file)

    def team_scores(self, team_scores, time):
        """Store output of team scores to a JSON file"""
        output_filename = 'team_scores_{0}.json'.format(time)
        data = []
        for score in team_scores['fixtures']:
            if score['status'] == 'FINISHED':
                item = {'date': score["date"].split('T')[0],
                        'homeTeamName': score['homeTeamName'],
                        'goalsHomeTeam': score['result']['goalsHomeTeam'],
                        'goalsAwayTeam': score['result']['goalsAwayTeam'],
                        'awayTeamName': score['awayTeamName']}
                data.append(item)
        with open(output_filename, 'w') as json_file:
            json.dump({'team_scores': data}, json_file)

    def standings(self, league_table, league):
        """Store output of league standings to a JSON file"""
        output_filename = '{0}_standings.json'.format(league)
        data = []
        for team in league_table['standing']:
            item = {'position': team['position'], 'teamName': team['teamName'],
                    'playedGames': team['playedGames'], 'goalsFor': team['goals'],
                    'goalsAgainst': team['goalsAgainst'], 'goalDifference': team['goalDifference'],
                    'points': team['points']}
            data.append(item)
        with open(output_filename, 'w') as json_file:
            json.dump({'standings': data}, json_file)

    def league_scores(self, total_data, time):
        """Store output of fixtures based on league and time to a JSON file"""
        output_filename = 'league_scores_{0}.json'.format(time)
        data = []
        for league, score in supported_leagues(total_data, self):
            item = {'league': league, 'homeTeamName': score['homeTeamName'],
                    'goalsHomeTeam': score['result']['goalsHomeTeam'],
                    'goalsAwayTeam': score['result']['goalsAwayTeam'],
                    'awayTeamName': score['awayTeamName']}
            data.append(item)
        with open(output_filename, 'w') as json_file:
            json.dump({'league_scores': data, 'time': time}, json_file)

    def league_header(self, league_name):
        pass
