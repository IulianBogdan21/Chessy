import unittest

from Chess import engine


class TestPinsChecks(unittest.TestCase):

    # white to move - confirm that one pawn is pinned to move because of ulterior direct check
    def test_pawn_pin(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        new_board = [
            ["bR", "bN", "bB", "bQ", "bK", "--", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "--", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "bp", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "bB", "--", "--", "--", "wp", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "--", "--", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        game_state.set_board(new_board)
        is_king_in_check, pins, checks = game_state.check_for_pins_and_checks()
        pinned_piece_row = pins[0][0]
        pinned_piece_column = pins[0][1]
        pinned_direction = (pins[0][2], pins[0][3])
        self.assertFalse(is_king_in_check)
        self.assertEqual(pinned_piece_row, 6)
        self.assertEqual(pinned_piece_column, 3)
        self.assertEqual(pinned_direction, (-1, -1))

    # white to move - test that white bishop is pinned and cannot move
    def test_bishop_pin(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        game_state.current_castling_rights.white_king_side =  False
        game_state.current_castling_rights.black_king_side =  False
        new_board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "--"],
            ["--", "--", "bp", "bp", "bp", "--", "bp", "--"],
            ["bp", "bp", "--", "--", "bR", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "bp"],
            ["--", "--", "--", "wp", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "wN", "--", "wp"],
            ["wp", "wp", "--", "--", "wB", "wp", "wp", "wR"],
            ["wR", "wN", "wB", "wQ", "wK", "--", "--", "--"]
        ]
        game_state.set_board(new_board)
        is_king_in_check, pins, checks = game_state.check_for_pins_and_checks()
        pinned_piece_row = pins[0][0]
        pinned_piece_column = pins[0][1]
        pinned_direction = (pins[0][2], pins[0][3])
        self.assertFalse(is_king_in_check)
        self.assertEqual(pinned_piece_row, 6)
        self.assertEqual(pinned_piece_column, 4)
        self.assertEqual(pinned_direction, (-1, 0))

    # test that black king is in check
    def test_black_king_in_check(self):
        game_state = engine.GameState()
        game_state.white_to_move = False
        new_board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "--", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "bp", "--", "--", "--", "--"],
            ["--", "wB", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "wp", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "--", "wN", "wR"]
        ]
        game_state.set_board(new_board)
        is_king_in_check, pins, checks = game_state.check_for_pins_and_checks()
        checking_piece_row = checks[0][0]
        checking_piece_column = checks[0][1]
        check_direction = (checks[0][2], checks[0][3])
        self.assertTrue(is_king_in_check)
        self.assertEqual(checking_piece_row, 3)
        self.assertEqual(checking_piece_column, 1)
        self.assertEqual(check_direction, (1, -1))

    # test that white king is in check
    def test_white_king_in_check(self):
        game_state = engine.GameState()
        game_state.white_to_move = True
        new_board = [
            ["bR", "bN", "bB", "bQ", "bK", "--", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "--", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "bp", "--", "--", "--"],
            ["--", "bB", "--", "wp", "wp", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "--", "--", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        game_state.set_board(new_board)
        is_king_in_check, pins, checks = game_state.check_for_pins_and_checks()
        checking_piece_row = checks[0][0]
        checking_piece_column = checks[0][1]
        check_direction = (checks[0][2], checks[0][3])
        self.assertTrue(is_king_in_check)
        self.assertEqual(checking_piece_row, 4)
        self.assertEqual(checking_piece_column, 1)
        self.assertEqual(check_direction, (-1, -1))

