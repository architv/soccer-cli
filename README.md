<p align="center">
  <img src="http://i.imgur.com/F9zuexe.jpg" width="500px" />
</p>

Soccer CLI
=====

[![Join the chat at https://gitter.im/architv/soccer-cli](https://badges.gitter.im/architv/soccer-cli.svg)](https://gitter.im/architv/soccer-cli?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![PyPI version](https://badge.fury.io/py/soccer-cli.svg)](http://badge.fury.io/py/soccer-cli)

Soccer for Hackers - a CLI for all the football scores. 

![](http://i.imgur.com/9QbcUrj.gif)

Install
=====

An API key from [football-data.org](http://api.football-data.org/) will be required and you can register for one [here](http://api.football-data.org/register).

### Using `pip`

```bash
$ pip install soccer-cli
```

Set your API key in an environment variable `SOCCER_CLI_API_TOKEN`

For example:

```bash
export SOCCER_CLI_API_TOKEN="<YOUR_API_TOKEN>"
```

### Build from source

```bash
$ git clone git@github.com/architv/soccer-cli.git
$ cd soccer-cli
$ python setup.py install
```

You can set the API key using an environment variable as shown above or create a file `.soccer-cli.ini` in your home folder (`/home/username/.soccer-cli.ini`) that contains only your API token, such that:

```bash
$ cat /home/username/.soccer-cli.ini
<YOUR_API_TOKEN>
```

#### Note:
Currently supports Linux, Mac OS X, NetBSD, FreeBSD and Windows.

To get colorized terminal output on Windows, make sure to install [ansicon](https://github.com/adoxa/ansicon/releases/latest) and [colorama](https://pypi.python.org/pypi/colorama).

Usage
====

### Get standings for a league

```bash
$ soccer --standings --league=EPL # EPL is the league code for English Premier League
```

### Get scores for a particular team

```bash
$ soccer --team=MUFC # MUFC is the team code for Manchester United
$ soccer --team=PSG --time=10 # scores for all the Paris Saint-Germain games over the past 10 days
```

### Get upcoming fixtures

```bash
$ soccer --time 5 --upcoming # get upcoming fixtures for next 5 days
$ soccer --time 5 --upcoming --use12hour # upcoming fixture for next 5 days with timings in 12 hour format
```

### Get scores for live games

```bash
$ soccer --live
```

### Get scores for a particular league

```bash
$ soccer --league=BL # BL is the league code for Bundesliga
$ soccer --league=FL --time=15 # get scores for all the French Ligue games over the past 15 days
```

### Get information about players of a team

```bash
$ soccer --team=JUVE --players
```

### Get scores for all seven leagues with a set time period

```bash
$ soccer --time=10 # scores for all the seven leagues over the past 10 days
```

### Get the output in csv or json

```bash
$ soccer --league EPL --standings --csv # prints the output in csv format
$ soccer --league EPL --standings --json # prints the output in json format
```

### Store the ouput in a file

```bash
$ soccer --league EPL --standings --csv -o 'standings.csv' # stores the ouput in scv format in `standings.csv`
```

### Help
```bash
$ soccer --help
```
### List of supported leagues and their league codes

- Europe:
  - CL: Champions League
- England:
  - EPL: Premier League
  - EL1: League One
- France:
  - FL: Ligue 1
  - FL2: Ligue 2
- Germany:
  - BL: Bundesliga
  - BL2: 2. Bundesliga
  - BL3: 3. Liga
- Italy:
  - SA: Serie A 
- Netherlands:
  - DED: Eredivisie
- Portugal:
  - PPL: Primeira Liga
- Spain:
  - LLIGA: La Liga
  - SD: Segunda Division

### Team and team codes

For a full list of supported team and team codes [see this](soccer/teams.json).

Demo
====

### Standings
![standings](http://i.imgur.com/voyWLQE.gif)

### Live scores
![](http://i.imgur.com/EX9GMAM.gif)

### Team scores
![](http://i.imgur.com/QfvH8QL.png)

### Output in json format
![](http://i.imgur.com/jqGhLia.gif)

Todo
====
- [ ] Enable cache
- [ ] Add more test cases
- [x] Add fixtures for UEFA Champions League
- [ ] Add league filter for live scores
- [x] Color coding for Europa league and differentiation between straight CL and CL playoff spots, and the same for EL spots
- [x] Add support for team line up
- [ ] A built in watch feature so you can run once with --live and just leave the program running.

Licence
====
Open sourced under [MIT License](LICENSE)

Support
====
If you like my work, please support the project by donating.

- https://gratipay.com/~architv
