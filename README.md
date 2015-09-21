<p align="center">
  <img src="http://i.imgur.com/F9zuexe.jpg" width="500px" />
</p>

Soccer CLI
=====

[![PyPI version](https://badge.fury.io/py/soccer-cli.svg)](http://badge.fury.io/py/soccer-cli)

Soccer for Hackers - a CLI for all the football scores. 

![](http://i.imgur.com/9QbcUrj.gif)

Install
=====

### Using `pip`

```bash
$ pip install soccer-cli
````

### Build from source

For building from source, you'll need to get your API key from [here](http://api.football-data.org/register) and create a file `config.py` in the soccer package directory (`soccer/config.py`) with the single line
```
config = {
    "SOCCER_CLI_API_TOKEN": "<YOUR_API_TOKEN>",
}
```

An alternate option of storing your API key is to store it as an environment variable. For Linux and Mac OS X, you can do the following:
```
export SOCCER_CLI_API_TOKEN="<YOUR_API_TOKEN>"
```

```bash
$ git clone git@github.com:architv/soccer-cli.git
$ cd soccer-cli
$ python setup.py install
```

#### Note:
Currently supports Linux, Mac OS X, NetBSD and FreeBSD.

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

### Get scores for live games

```bash
$ soccer --live
```

### Get scores for a particular league

```bash
$ soccer --league=BL # BL is the league code for Bundesliga
$ soccer --league=FL --time=15 # get scores for all the French Ligue games over the past 15 days
```

### Get scores for all seven leagues with a set time period

```bash
$ soccer --time=10 # scores for all the seven leagues over the past 10 days
```

### Help
```bash
$ soccer --help
```
### List of supported leagues and their league codes

- BL: Bundesliga (German League)
- FL: Ligue 1 (French League)
- EPL: English Premier League
- LLIGA: Liga BBVA (Spanish League)
- SA: Serie A  (Italian League)
- PPL: Primeira Liga (Portuguese League)
- DED: Eredivisie (Dutch League)
- CL: Champions League

### Team and team codes

For a full list of supported team and team codes [see this](teamcodes.json).

Demo
====

### Standings
![standings](http://i.imgur.com/NURexbN.gif)

### Live scores
![](http://i.imgur.com/EX9GMAM.gif)

### Team scores
![](http://i.imgur.com/QfvH8QL.png)

Todo
====
- [ ] Enable cache
- [ ] Add more test cases
- [x] Add fixtures for UEFA Champions League
- [ ] Add league filter for live scores
- [x] Color coding for Europa league and differentiation between straight CL and CL playoff spots, and the same for EL spots
- [ ] Add support for team line up

Licence
====
Open sourced under [MIT License](LICENSE)

Support
====
If you like my work, please support the project by donating.

- https://gratipay.com/~architv
