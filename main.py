#!/usr/bin/env python

import requests
import click
import leagueids
import authtoken
import json
import teamnames
import liveapi

BASE_URL = 'http://api.football-data.org/alpha/'
LIVE_URL = liveapi.LIVE_API
LEAGUE_IDS = leagueids.LEAGUE_IDS
headers = {
	'X-Auth-Token': authtoken.API_TOKEN
}
TEAM_NAMES = teamnames.team_names

def get_live_scores():
	""" Gets the live scores """

	req = requests.get(LIVE_URL)
	if req.status_code == 200:
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
			click.secho('%d %-10s\t' % (game["goalsAwayTeam"], game["awayTeamName"]), fg="blue", nl=False)
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
		if req.status_code == 200:
			print_team_scores(req.json())
		else:
			click.secho("No data for the team. Please check the team code.", fg="red", bold=True)
	else:
		click.secho("No data for the team. Please check the team code.", fg="red", bold=True)

def print_team_scores(team_scores):
	""" Prints the teams scores in a pretty format """

	for score in team_scores["fixtures"]:
		if score["status"] == "FINISHED":
			click.echo()
			click.secho("%s\t" % score["date"].split('T')[0], fg="green", nl=False)
			if score["result"]["goalsHomeTeam"] > score["result"]["goalsAwayTeam"]:
				click.secho('%-20s %-5d' % (score["homeTeamName"], score["result"]["goalsHomeTeam"]), 
					bold=True, fg="red", nl=False)
				click.secho("vs\t", nl=False)
				click.secho('%d %-10s\t' % (score["result"]["goalsAwayTeam"], score["awayTeamName"]), fg="blue")
			else:
				click.secho('%-20s %-5d' % (score["homeTeamName"], score["result"]["goalsHomeTeam"]), 
					 fg="blue", nl=False)
				click.secho("vs\t", nl=False)
				click.secho('%d %-10s\t' % (score["result"]["goalsAwayTeam"], score["awayTeamName"]), bold=True, fg="red")
			click.echo()


def get_standings(league):
	""" Queries the API and gets the standings for a particular league """

	if not league:
		click.secho("Please specify a league. Example --standings --league=EPL", fg="red", bold=True)
		return

	league_id = LEAGUE_IDS[league]
	req = requests.get('{base_url}soccerseasons/{id}/leagueTable'.format(
			base_url=BASE_URL, id=league_id), headers=headers)
	if req.status_code == 200:
		print_standings(req.json())
	else:
		click.secho("No standings availble for {league}.".format(league=league), fg="red", bold=True)

def print_standings(league_table):
	""" Prints the league standings in a pretty way """

	click.secho("{position:6}  {team:30}    {played:10}    {goaldiff:10}    {points:10}".format(
					position="POS", team="CLUB", played="PLAYED", 
					goaldiff="GOAL DIFF", points="POINTS"
			))

	for team in league_table["standing"]:
		if team["position"] <= 4:
			click.secho("{position:6}  {team:30}    {played:10}    {goaldiff:10}    {points:10}".format(
					position=str(team["position"]), team=u''.join(team["teamName"]).encode('utf-8'), played=str(team["playedGames"]), 
					goaldiff=str(team["goalDifference"]), points=str(team["points"])
				), bold=True, fg="green")
		elif 5 <= team["position"] <= 17:
			click.secho("{position:6}  {team:30}    {played:10}    {goaldiff:10}    {points:10}".format(
					position=str(team["position"]), team=u''.join(team["teamName"]).encode('utf-8'), played=str(team["playedGames"]), 
					goaldiff=str(team["goalDifference"]), points=str(team["points"])
				), fg="blue")
		else:
			click.secho("{position:6}  {team:30}    {played:10}    {goaldiff:10}    {points:10}".format(
					position=str(team["position"]), team=u''.join(team["teamName"]).encode('utf-8'), played=str(team["playedGames"]), 
					goaldiff=str(team["goalDifference"]), points=str(team["points"])
				), fg="red")

		# print "{position}. {team_name}".format(position=team["position"], team_name=team["teamName"])

def get_scores(league, time):
	""" Queries the API and fetches the scores for fixtures based upon the league and time parameter """

	if league:
		league_id = LEAGUE_IDS[league]
		fixtures_results = requests.get('{base_url}soccerseasons/{id}/fixtures?timeFrame=p{time}'.format(
			base_url=BASE_URL, id=league_id, time=str(time)), headers=headers).json()
		
		# no fixtures in the past wee. display a help message and return
		if len(fixtures_results["fixtures"]) == 0:
			click.secho("No Champions League matches in the past week.", fg="red", bold=True)
			return

		print_league_scores(fixtures_results)
		return

	fixtures_results = requests.get('{base_url}fixtures?timeFrame=p{time}'.format(
		base_url=BASE_URL, time=str(time)), headers=headers).json()
	print_league_scores(fixtures_results)

def print_league_scores(total_data):
	""" Prints the data in a pretty format """

	for data in total_data["fixtures"]:
		if data["result"]["goalsHomeTeam"] > data["result"]["goalsAwayTeam"]:
			click.secho('%-20s %-5d' % (data["homeTeamName"], data["result"]["goalsHomeTeam"]), 
				bold=True, fg="red", nl=False)
			click.secho("vs\t", nl=False)
			click.secho('%d %-10s\t' % (data["result"]["goalsAwayTeam"], data["awayTeamName"]), fg="blue")
		else:
			click.secho('%-20s %-5d' % (data["homeTeamName"], data["result"]["goalsHomeTeam"]), 
				 fg="blue", nl=False)
			click.secho("vs\t", nl=False)
			click.secho('%d %-10s\t' % (data["result"]["goalsAwayTeam"], data["awayTeamName"]), bold=True, fg="red")
		click.echo()


@click.command()
@click.option('--live', is_flag=True, help= 'Shows live scores from various leagues')
@click.option('--standings', is_flag=True, help= 'Standings for a particular league')
@click.option('--league', '-league', type=click.Choice(LEAGUE_IDS.keys()), 
	help= (
		"Choose the league whose fixtures you want to see. Bundesliga(BL), Premier League(EPL), La Liga (LLIGA)," 
	 	"Serie A(SL), Ligue 1(FL), Eredivisie(DED), Primeira Liga(PPL), Champions League(CL)')"
	)
)
@click.option('--team', type=click.Choice(TEAM_NAMES.keys()), 
	help= (
		"Choose the team whose fixtures you want to see. See the various team codes listed on README')"
	)
)
@click.option('--time', default=6, 
	help= 'The number of days for which you want to see the scores')

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
