import datetime
import uuid
import cPickle as pickle
from werkzeug.routing import BaseConverter


# Source: https://gist.github.com/ekayxu/5743138
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def unique_id(num=6):
    "Generates quasi unique id"
    return str(uuid.uuid1())[:num]


def set_value(red, key, value):
    red.set(key, pickle.dumps(value))


def get_value(red, key):
    pickled_value = red.get(key)
    if pickled_value is None:
        return None
    try:
        return pickle.loads(pickled_value)
    except pickle.UnpicklingError:
        red.delete(key) # Delete corrupted keys
        return None


def get_board(red, game_id):
    board = get_value(red, game_id)
    if board is not None:
        return board
    board = init_board(game_id)
    update_board(red, game_id, board)
    return board


def init_board(game_id):
    "Returns board state for the game"
    rows = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append({
                "id": "c{}{}".format(i, j),
                "mark": ""
            })
        rows.append(row)
    board = {
        "rows": rows,
        "winner": None,
        "next_turn": "user",
        "created_at": int(datetime.datetime.now().strftime("%s")) # timestamp
    }
    return board


def update_board(red, game_id, board):
    set_value(red, game_id, board)


def set_cell(board, move=None, mark=None, winner=None, next_turn=None):
    if (move is not None and mark is not None):
        board["rows"][move[0]][move[1]]["mark"] = mark
    if winner is not None:
        board["winner"] = winner
    if next_turn is not None:
        board["next_turn"] = next_turn


def to_status(board):
    winner = board.get("winner", None)
    d = {
        "server": "Server won",
        "user": "User won",
        "tie": "Tie"
    }
    try:
        status = d[winner]
        if status is None:
            return "In progress"
        return status
    except KeyError:
        return ""


def to_date(board):
    created_at = board.get("created_at", None)
    if created_at is None:
        return ""
    return datetime.datetime.fromtimestamp(created_at).strftime("%b %d %Y, %I:%M%p")

