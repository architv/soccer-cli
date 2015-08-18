import requests
import click
import leagueids
import authtoken
import json

BASE_URL = 'http://api.football-data.org/alpha/'
LIVE_URL = ''
LEAGUE_IDS = leagueids.LEAGUE_IDS
headers = {
	'X-Auth-Token': authtoken.API_TOKEN
}

with open('teamnames.json', 'r') as teamnames:
	TEAM_NAMES = json.loads(teamnames.read())

def get_team_scores(team, time):
	""" Queries the API and gets the particular team scores """

	team_id = TEAM_NAMES.get(team, None)
	if team_id:
		team_scores = requests.get('{base_url}teams/{team_id}/fixtures/'.format(
			base_url=BASE_URL, team_id=team_id), headers=headers).json()
		print_team_scores(team_scores)
	else:
		print "No data for the team. Please check the team code."

def print_team_scores(team_scores):
	""" Prints the teams scores in a pretty format """

	for score in team_scores["fixtures"]:
		if score["status"] == "FINISHED":
			print score["date"].split('T')[0]
			print score["homeTeamName"] + " " + str(score["result"]["goalsHomeTeam"]) + " vs "  + str(score["result"]["goalsAwayTeam"]) + " " + score["awayTeamName"] 


def get_standings(league):
	""" Queries the API and gets the standings for a particular league """

	league_id = LEAGUE_IDS[league]
	league_table = requests.get('{base_url}soccerseasons/{id}/leagueTable'.format(
			base_url=BASE_URL, id=league_id), headers=headers).json()
	print_standings(league_table)

def print_standings(league_table):

	for team in league_table["standing"]:
		print "{position}. {team_name}".format(position=team["position"], team_name=team["teamName"])

def get_scores(league, time):
	""" Queries the API and fetches the scores for fixtures based upon the league and time parameter """

	if league:
		league_id = LEAGUE_IDS[league]
		fixtures_results = requests.get('{base_url}soccerseasons/{id}/fixtures?timeFrame=p{time}'.format(
			base_url=BASE_URL, id=league_id, time=str(time)), headers=headers).json()
		pretty_print(fixtures_results)
		return

	fixtures_results = requests.get('{base_url}fixtures?timeFrame=p{time}'.format(
		base_url=BASE_URL, time=str(time)), headers=headers).json()
	pretty_print(fixtures_results)

def pretty_print(total_data):
	""" Prints the data in a pretty format """

	for data in total_data["fixtures"]:
		# midstring = "vs"
		if data["result"]["goalsHomeTeam"] > data["result"]["goalsAwayTeam"]:
			click.secho('%-20s %-5d' % (data["homeTeamName"], data["result"]["goalsHomeTeam"]), 
				bold=True, fg="red", nl=False)
			click.secho("vs\t", nl=False)
			click.secho('%d %-10s\t' % (data["result"]["goalsAwayTeam"], data["awayTeamName"]), fg="blue")
		else:
			click.secho('%-20s %-5d' % (data["homeTeamName"], data["result"]["goalsHomeTeam"]), 
				 fg="blue", nl=False)
			click.secho("vs\t", nl=False)
			click.secho('%d %-10s\t' % (data["result"]["goalsAwayTeam"], data["awayTeamName"]),bold=True, fg="red")
		click.echo()


@click.command()
@click.option('--standings', is_flag=True, help= 'Standings for a particular league')
@click.option('--league', '-league', type=click.Choice(LEAGUE_IDS.keys()), 
	help= (
		"Choose the league whose fixtures you want to see. Bundesliga(BL), Premier League(EPL), La Liga (LLIGA)," 
	 	"Serie A(SL), Ligue 1(FL), Eredivisie(DED), Primeira Liga(PPL)')"
	)
)
@click.option('--team', type=click.Choice(TEAM_NAMES.keys()), 
	help= (
		"Choose the team whose fixtures you want to see. See the various team codes listed on README')"
	)
)
@click.option('--time', '-t', default=6, 
	help= 'The number of days for which you want to see the scores')

def main(league, time, standings, team):
	""" A CLI for live and past football scores from various leagues """

	if standings:
		get_standings(league)
		return

	if team:
		get_team_scores(team, time)
		return

	get_scores(league, time)

if __name__ == '__main__':
	main()