<p align="center">
  <img src="http://i.imgur.com/F9zuexe.jpg" width="500px" />
</p>

Soccer CLI
=====

Soccer for Hackers - a CLI for all the football scores. 

![](http://i.imgur.com/NFzF6rA.png)

Install
=====

### Using Pip

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

Demo
====
