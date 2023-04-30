import random

global next_move

piece_score = {
    "K": 0,
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1
}

# create score arrays for all pieces

knight_scores = [[1, 1, 1, 1, 1, 1, 1, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 3, 3, 3, 2, 1],
                 [1, 2, 2, 2, 2, 2, 2, 1],
                 [1, 1, 1, 1, 1, 1, 1, 1]
                 ]

bishop_scores = [[4, 3, 2, 1, 1, 2, 3, 4],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [4, 3, 2, 1, 1, 2, 3, 4]
                 ]

queen_scores = [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]
                ]

rook_scores = [[4, 3, 4, 4, 4, 4, 3, 4],
               [4, 4, 4, 4, 4, 4, 4, 4],
               [1, 1, 2, 3, 3, 2, 1, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 1, 2, 2, 2, 2, 1, 1],
               [4, 4, 4, 4, 4, 4, 4, 4],
               [4, 3, 4, 4, 4, 4, 3, 4]
               ]

white_pawn_scores = [[8, 8, 8, 8, 8, 8, 8, 8],
                     [8, 8, 8, 8, 8, 8, 8, 8],
                     [5, 6, 6, 7, 7, 6, 6, 5],
                     [2, 3, 3, 5, 5, 3, 3, 2],
                     [1, 2, 3, 4, 4, 3, 2, 1],
                     [1, 1, 2, 3, 3, 2, 1, 1],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [0, 0, 0, 0, 0, 0, 0, 0]
                     ]

black_pawn_scores = [[0, 0, 0, 0, 0, 0, 0, 0],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [1, 1, 2, 3, 3, 2, 1, 1],
                     [1, 2, 3, 4, 4, 3, 2, 1],
                     [2, 3, 3, 5, 5, 3, 3, 2],
                     [5, 6, 6, 7, 7, 6, 6, 5],
                     [8, 8, 8, 8, 8, 8, 8, 8],
                     [8, 8, 8, 8, 8, 8, 8, 8]
                     ]

piece_position_scores = {"N": knight_scores,
                         "Q": queen_scores,
                         "B": bishop_scores,
                         "R": rook_scores,
                         "bp": black_pawn_scores,
                         "wp": white_pawn_scores
                         }

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

"""
find random move for AI
"""


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


"""
method that calls for negamax search
"""


def find_best_move(game_state, valid_moves, return_queue):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    find_move_negamax_alpha_beta(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                                 1 if game_state.white_to_move else -1)
    return_queue.put(next_move)


"""
negamax algorithm for finding best move
"""


def find_move_negamax_alpha_beta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_board(game_state)

    maximum_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        # the - is crucial because we switch the sides using that -
        score = -find_move_negamax_alpha_beta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > maximum_score:
            maximum_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undo_move()
        # pruning happens
        if maximum_score > alpha:
            alpha = maximum_score
        if alpha >= beta:
            break

    return maximum_score


"""
method that scores the board considering the material
evaluation function basically
a positive score is good for white, a negative one is good for black
"""


def score_board(game_state):
    # check for checkmate before evaluating position + check for stalemate
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif game_state.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(game_state.board)):
        for column in range(len(game_state.board[row])):
            square = game_state.board[row][column]
            if square != "--":
                # score it positionally
                piece_position_score = 0
                if square[1] != "K":
                    # for pawns
                    if square[1] == "p":
                        piece_position_score = piece_position_scores[square][row][column]
                    else:
                        piece_position_score = piece_position_scores[square[1]][row][column]

                if square[0] == 'w':
                    score += piece_score[square[1]] + piece_position_score * .1
                elif square[0] == 'b':
                    score -= piece_score[square[1]] + piece_position_score * .1
    return score
