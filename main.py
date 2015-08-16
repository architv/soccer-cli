import requests

BASE_URL = 'http://www.football-data.org/'
LIVE_URL = ''

def get_scores():
	all_data = requests.get(BASE_URL + 'soccerseasons/398/fixtures?timeFrame=p6').json()
	for data in all_data:
		print data["homeTeam"] + " " + str(data["goalsHomeTeam"]) + " vs "  + str(data["goalsAwayTeam"]) + " " + data["awayTeam"] 

if __name__ == '__main__':
	get_scores()