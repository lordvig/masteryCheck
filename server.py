from mastery import get_mastery_data, get_champion_name, get_league_data, get_current_game

from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/player/<name>")
def player(name):
    mastery = get_mastery_data(name)
    league = get_league_data(name)
    data = {'champ_mastery': mastery, 'league_data': league, 'name': name}
    return render_template("player.html", data=data)


@app.route("/test/champ/<int:champid>")
def champ_data(champid):
    return render_template("test.html", data=get_champion_name(champid))


@app.route("/current/<name>")
def current_game(name):
    try:
        current = get_current_game(name)
        data = current
        return render_template("currentGame.html", data=data)
    except Exception as e:
        print(e)
        return render_template("test.html", data="Couldn't get current game")


@app.route("/riot.txt")
def riot_perm():
    return '63f43679-103b-410d-8c27-788a863b3012'
