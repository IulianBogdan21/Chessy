import unittest

from Chess import engine


class TestPiecesMoves(unittest.TestCase):

    # check all the generated valid moves of a rook from a given position
    def test_rook_moves(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        game_state.current_castling_rights.white_king_side = False
        new_board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["--", "--", "bp", "bp", "bp", "bp", "--", "--"],
            ["bp", "bp", "--", "--", "--", "--", "bp", "bp"],
            ["--", "--", "--", "--", "wR", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "wp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "--"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "--"]
        ]
        game_state.set_board(new_board)
        moves = []
        expected_moves = ["Re6", "Rxe7", "Rd5", "Rc5", "Rb5", "Ra5", "Re4", "Re3", "Rf5", "Rg5", "Rh5"]
        game_state.get_rook_moves(3, 4, moves)
        for move in moves:
            self.assertTrue(expected_moves.__contains__(str(move)))

    # check all the generated valid moves of a knight from a given position
    def test_knight_moves(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        new_board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "--", "--", "bp", "bp", "bp"],
            ["--", "--", "--", "bp", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "wp"],
            ["--", "--", "--", "--", "--", "wN", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "--"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "--", "wR"]
        ]
        game_state.set_board(new_board)
        moves = []
        expected_moves = ["Nxe5", "Ng5", "Nd4", "Nh2", "Ng1"]
        game_state.get_knight_moves(5, 5, moves)
        for move in moves:
            self.assertTrue(expected_moves.__contains__(str(move)))

    # check all the generated valid moves of a bishop from a given position
    def test_bishop_moves(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        new_board = [
            ["bR", "--", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bN", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "wB", "--", "bp", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "wN", "--", "--"],
            ["wp", "wp", "wp", "wp", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "--", "wN", "wR"]
        ]
        game_state.set_board(new_board)
        moves = []
        expected_moves = ["Ba6", "Bc6", "Bxd7", "Ba4", "Bc4", "Bd3", "Be2", "Bf1"]
        game_state.get_bishop_moves(3, 1, moves)
        for move in moves:
            self.assertTrue(expected_moves.__contains__(str(move)))

    # check all the generated valid moves of a king from a given position
    # main function that gets valid moves from a king does not include castling, castling is treated as a special move
    def test_king_moves(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        new_board = [
            ["bR", "--", "bB", "bQ", "bK", "--", "bN", "bR"],
            ["--", "--", "bp", "bp", "bB", "bp", "bp", "--"],
            ["bp", "bp", "bN", "--", "--", "--", "--", "bp"],
            ["--", "wB", "--", "--", "bp", "--", "--", "--"],
            ["--", "--", "wp", "--", "wp", "--", "--", "--"],
            ["--", "wQ", "--", "wp", "--", "wN", "--", "--"],
            ["wp", "wp", "--", "--", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "--", "wK", "--", "--", "wR"]
        ]
        game_state.set_board(new_board)
        moves = []
        expected_moves = ["Kd2", "Ke2", "Kd1", "Kf1", "O-O"]
        game_state.get_king_moves(7, 4, moves)
        game_state.get_king_side_castle_moves(7, 4, moves)
        for move in moves:
            self.assertTrue(expected_moves.__contains__(str(move)))

    # check all the generated valid moves of a pawn from a given position
    # scenario where pawn can capture right, advance one position or capture enpassant
    def test_pawn_moves_first_scenario(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        game_state.enpassant_possible = (2, 4)
        new_board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "--", "bp", "--", "bp"],
            ["--", "--", "--", "--", "--", "--", "bp", "--"],
            ["--", "--", "--", "--", "bp", "wp", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "--", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        game_state.set_board(new_board)
        moves = []
        expected_moves = ["f6", "fxe6", "fxg6"]
        game_state.get_pawn_moves(3, 5, moves)
        for move in moves:
            self.assertTrue(expected_moves.__contains__(str(move)))

    # check all the generated valid moves of a pawn from a given position
    # scenario where pawn can capture left, advance one position or advance two positions
    def test_pawn_moves_second_scenario(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        new_board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "--", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "--", "bp", "--", "--", "--"],
            ["--", "--", "--", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        game_state.set_board(new_board)
        moves = []
        expected_moves = ["f3", "f4", "fxe3"]
        game_state.get_pawn_moves(6, 5, moves)
        for move in moves:
            self.assertTrue(expected_moves.__contains__(str(move)))