import unittest
from app import red
from app.strategy import Game
from app.tools import unique_id, get_board, set_cell
from app.const import USER_MARK, SERVER_MARK

# Integration tests for Tic Tac Toe game

class GameTestCase(unittest.TestCase):

    def setUp(self):
        # Create a new board
        self.game_id = unique_id()
        self.board = get_board(red, self.game_id)


    def test_redis_key(self):
        self.assertTrue(red.exists(self.game_id))


    def test_server_win(self):
        # Set board for server win
        user_move = [0, 1]
        # User moves
        set_cell(self.board, move=[0, 0], mark=USER_MARK)
        set_cell(self.board, move=[1, 0], mark=USER_MARK)
        # Server moves
        set_cell(self.board, move=[2, 0], mark=SERVER_MARK)
        set_cell(self.board, move=[1, 1], mark=SERVER_MARK)

        data = Game(self.board).handle_move(user_move)
        self.assertEqual(data["move"], [0, 2]) # Winning move
        self.assertEqual(data["winner"], "server")


    def test_server_block(self):
        # Set board for server block
        user_move = [0, 1]
        # User moves
        set_cell(self.board, move=[0, 0], mark=USER_MARK)
        # Server moves
        set_cell(self.board, move=[1, 1], mark=SERVER_MARK)

        data = Game(self.board).handle_move(user_move)
        self.assertEqual(data["move"], [0, 2])  # Blocking move
        self.assertTrue(not data.has_key("winner")) # No winner


    def tearDown(self):
        red.delete(self.game_id)


if __name__ == "__main__":
    unittest.main()