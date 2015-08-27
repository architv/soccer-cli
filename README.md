<p align="center">
  <img src="http://i.imgur.com/F9zuexe.jpg" width="500px" />
</p>

Soccer CLI
=====

Soccer for Hackers - a CLI for all the football scores. 

![](http://i.imgur.com/9QbcUrj.gif)

Install
=====

### Using `pip`

```bash
$ pip install soccer-cli
````

### Build from source

```bash
$ git clone git@github.com:architv/soccer-cli.git
$ cd soccer-cli
$ python setup.py install
```

Usage
====

### Get standings for a league

```bash
$ soccer --standings --league=EPL #EPL is the league code for English Premier League
```

### Get scores for a particular team

```bash
$ soccer --team=MUFC #MUFC is the team code for Manchester United
$ soccer --team=PSG --time=10 # scores for all the Paris Saint-Germain games over the past 10 days
```

### Get scores for live games

```bash
$ soccer --live
```

### Get scores for a particular league

```bash
$ soccer --league=BL # BL is the lague code for Bundesliga
$ soccer --league=FL --time=15 # get scores for all the French Ligue games over the apst 15 days
```

### Get scores for all seven leagues with a set time period

```bash
$ soccer soccer --time=10 # scores for all the seven leagues over the past 10 days
```

### Help
```bash
$ soccer --help
```
### List of supported leagues and their league codes

- BL: Bundesliga
- FL: French Ligue
- EPL: English Premier League
- LLIGA: Liga BBVA (Spanish League)
- SA: Seria A
- PPL: Primeira Liga
- DED: Eredivisie (Dutch League)

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
- [ ] Add fixtures for UEFA Champions League

Licence
====
Open sourced under [MIT License](LICENSE)

Support
====
If you like my work, please support the project by donating.

- https://gratipay.com/~architv

