import random

piece_score = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1
}
CHECKMATE = 1000
STALEMATE = 0

"""
find random move for AI
"""


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


"""
minmax without recursion to find best move based only on material
"""


def find_best_move(game_state, valid_moves):
    turn_multiplier = 1 if game_state.white_to_move else -1
    opponent_minmax_score = CHECKMATE
    best_player_move = None
    for player_move in valid_moves:
        game_state.make_move(player_move)
        opponent_moves = game_state.get_valid_moves()
        if game_state.stalemate:
            opponent_max_score = -STALEMATE
        elif game_state.checkmate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                game_state.make_move(opponent_move)
                game_state.get_valid_moves()
                if game_state.checkmate:
                    current_score = CHECKMATE
                elif game_state.stalemate:
                    current_score = STALEMATE
                else:
                    current_score = -turn_multiplier * score_material(game_state.board)
                if current_score > opponent_max_score:
                    opponent_max_score = current_score
                game_state.undo_move()
        if opponent_max_score < opponent_minmax_score:
            opponent_minmax_score = opponent_max_score
            best_player_move = player_move
        game_state.undo_move()
    return best_player_move


"""
method that scores the board considering the material
evaluation function but really basic
"""


def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]
    return score
