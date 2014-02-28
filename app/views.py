from flask import url_for, jsonify, render_template
from flask.ext.socketio import emit

from . import app, socketio, red
from .const import GAME_REGEX
from .strategy import Game
from .tools import unique_id, get_board, update_board, to_date, to_status

@app.route("/")
def index():
    game_keys = red.keys()
    try:
        game_keys.remove('')
    except ValueError:
        pass
    games = []
    for game_id in game_keys:
        board = get_board(red, game_id)
        games.append(dict(
            game_id=game_id,
            created_at=board.get("created_at", ""),
            created_label=to_date(board),
            status=to_status(board)
        ))
    games = sorted(games, key=lambda game: game["created_at"], reverse=True)
    return render_template("index.html", games=games)


@socketio.on("move:server", namespace="/game")
def handle_move(message):
    game_id = message["gameId"]
    board = get_board(red, game_id)
    data = Game(board).handle_move()
    update_board(red, game_id, board)
    emit("move:server", data)


@socketio.on("move:user", namespace="/game")
def handle_move(message):
    game_id = message["gameId"]
    user_move = [int(i) for i in message["move"]]
    board = get_board(red, game_id)
    data = Game(board).handle_move(user_move)
    update_board(red, game_id, board)
    emit("move:server", data)


@socketio.on("init", namespace="/game")
def handle_init(game_id):
    emit("init", get_board(red, game_id))


@app.route("/new", methods=["POST",])
def new():
    "Creates new game and redirect"
    game_id = unique_id()
    get_board(red, game_id) # Store game id
    return jsonify(dict(game_id=game_id))


@app.route('/<regex("{}"):game_id>'.format(GAME_REGEX))
def game(game_id):
    c = dict(game_id = game_id)
    return render_template("board.html", **c)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500
