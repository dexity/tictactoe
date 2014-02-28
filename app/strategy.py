
from .tools import set_cell
from .const import *

class Game(object):

    def __init__(self, board):
        self.board = board
        self.rows = self.board["rows"]

    def handle_move(self, user_move=None):
        "Returns move or winner or both"
        if user_move:
            # Check user move
            set_cell(self.board, move=user_move, mark=USER_MARK, next_turn=SERVER)
            if self._check_win(USER_MARK):
                set_cell(self.board, winner=USER)
                return dict(winner=USER)

        # Check server move
        smove = self._next_move()
        if smove is None:   # Tie
            set_cell(self.board, winner=TIE)
            return dict(winner=TIE)

        set_cell(self.board, move=smove, mark=SERVER_MARK, next_turn=USER)
        if self._check_win(SERVER_MARK):
            set_cell(self.board, winner=SERVER)
            return dict(winner=SERVER, move=smove)

        if not self._first_empty_spot(): # Tie
            set_cell(self.board, winner=TIE)
            return dict(winner=TIE, move=smove)

        return dict(move=smove)


    def _next_move(self):
        "Returns (row, col) tuple"
        # Win game
        move = self._get_empty_spot(SERVER_MARK)
        if move:
            return move
        # Block user
        move = self._get_empty_spot(USER_MARK)
        if move:
            return move

        # Fork
        move = self._fork_cell(SERVER_MARK)
        if move:
            return move

        # Block opponent fork
        move = self._fork_cell(USER_MARK)
        if move:
            return move

        # Block center
        if self.rows[1][1]["mark"] == "":
            return [1, 1]

        # Opposite center
        move = self._get_corner(True)
        if move:
            return move

        # Empty corner
        move = self._get_corner(False)
        if move:
            return move

        # Whatever is left
        move = self._first_empty_spot()
        if move:
            return move
        return None


    def _get_empty_spot(self, mark):
        for i in range(3):
            move = self._get_cell(i, 0, i, 1, i, 2, mark)
            if move:
                return move
            move = self._get_cell(0, i, 1, i, 2, i, mark)
            if move:
                return move

        move = self._get_cell(0, 0, 1, 1, 2, 2, mark)
        if move:
            return move
        move = self._get_cell(2, 0, 1, 1, 0, 2, mark)
        if move:
            return move
        return None


    def _is_corner(self, i, j):
        return (i == 0 and j == 0) or (i == 0 and j == 2) or \
            (i == 2 and j == 0) or (i == 2 and j == 2)


    def _fork_cell(self, mark):
        "Get better fork cell"
        best_move = None
        best_score = 0
        for i in range(3):
            curr_i = i
            for j in range(3):
                curr_move = [curr_i, j]
                curr_row = self.rows[curr_i]
                curr_cell = curr_row[j]
                curr_score = 0
                if not curr_cell["mark"] == "":
                    continue
                row_str = "{}{}{}".format(curr_row[0]["mark"], curr_row[1]["mark"], curr_row[2]["mark"])
                if row_str == mark:
                    curr_score += 1
                col_str = "{}{}{}".format(self.rows[0][j]["mark"],
                                  self.rows[1][j]["mark"], self.rows[2][j]["mark"])
                if col_str == mark:
                    curr_score += 1
                if self._is_corner(i, j) and i != 1 and j != 1:
                    last_i = 2
                    last_j = 2
                    if i + 2 > 2:
                        last_i = 0
                    if j + 2 > 2:
                        last_j = 0
                    diag_str = "{}{}{}".format(curr_cell["mark"],
                                    self.rows[1][1]["mark"], self.rows[last_i][last_j]["mark"])
                    if diag_str == mark:
                        curr_score += 1
                if i == 1 and j == 1:
                    diag_str1 = "{}{}{}".format(self.rows[0][0]["mark"],
                                    self.rows[1][1]["mark"], self.rows[2][2]["mark"])
                    diag_str2 = "{}{}{}".format(self.rows[0][2]["mark"],
                                    self.rows[1][1]["mark"], self.rows[2][0]["mark"])
                    if diag_str1 == mark:
                        curr_score += 1
                    if diag_str2 == mark:
                        curr_score += 1

                if curr_score > best_score:
                    best_score = curr_score
                    best_move = curr_move

        if best_score > 1:
            return best_move
        return None


    def _get_corner(self, flag):
        "Returns corner cell"
        if "{}{}".format(self.rows[0][0]["mark"], self.rows[2][2]["mark"]) == USER_MARK:
            if self.rows[0][0]["mark"] == USER_MARK:
                return [2, 2]
            else:
                return [0, 0]
        if "{}{}".format(self.rows[2][0]["mark"], self.rows[0][2]["mark"]) == USER_MARK:
            if self.rows[2][0]["mark"] == USER_MARK:
                return [0, 2]
            else:
                return [2, 0]

        if not flag:
            for i in range(3):
                for j in range(3):
                    if self._is_corner(i, j) and self.rows[i][j]["mark"] == "":
                        return [i, j]
        return None


    def _first_empty_spot(self):
        for i in range(3):
            for j in range(3):
                if self.rows[i][j]["mark"] == "":
                    return [i, j]
        return None


    def _check_win(self, mark):
        strike = mark*3
        for i in range(3):
            # Horizontal
            if "{}{}{}".format(self.rows[i][0]["mark"],
               self.rows[i][1]["mark"], self.rows[i][2]["mark"]) == strike:
                return True
            # Vertical
            if "{}{}{}".format(self.rows[0][i]["mark"],
               self.rows[1][i]["mark"], self.rows[2][i]["mark"]) == strike:
                return True
        # Diagonal
        if "{}{}{}".format(self.rows[0][0]["mark"],
           self.rows[1][1]["mark"], self.rows[2][2]["mark"]) == strike:
            return True

        if "{}{}{}".format(self.rows[2][0]["mark"],
           self.rows[1][1]["mark"], self.rows[0][2]["mark"]) == strike:
            return True
        return False


    def _get_cell(self, i1, j1, i2, j2, i3, j3, mark):
        text = mark*2
        if not "{}{}{}".format(self.rows[i1][j1]["mark"],
            self.rows[i2][j2]["mark"], self.rows[i3][j3]["mark"]) == text:
            return None
        if self.rows[i1][j1]["mark"] == "":
            return [i1, j1]
        if self.rows[i2][j2]["mark"] == "":
            return [i2, j2]
        if self.rows[i3][j3]["mark"] == "":
            return [i3, j3]
        return None



