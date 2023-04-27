"""
responsible for storing all information about the current state of a chess game
responsible for determining the valid moves at the current state
will keep a move log
"""


class GameState:
    def __init__(self):
        # board is a 8x8 2 dimensional list + each element has 2 characters
        # first character = colour of the piece : black(b) or white(w)
        # second character = type of the piece : King(K), Queen(Q), Rook(R), Bishop(B), Knight(N), Pawn(P)
        # an empty space with no characters is marked by --
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.is_king_in_check = False
        # a list of all current pins
        self.pins = []
        # a list of all current checks
        self.checks = []
        # square coordinates where en passant capture is possible
        self.enpassant_possible = ()
        self.checkmate = False
        self.stalemate = False
        self.current_castling_rights = CastleRights(True, True, True, True)
        # we need to create new castle right objects when we append to log because of reference issues
        self.castle_rights_log = [CastleRights(self.current_castling_rights.white_king_side,
                                               self.current_castling_rights.black_king_side,
                                               self.current_castling_rights.white_queen_side,
                                               self.current_castling_rights.black_queen_side)]

    """
    function takes a move as parameter and executes it
    castling, en passant and pawn promotion not working yet
    """

    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved
        # add move to history of moves
        self.move_log.append(move)
        # update the location of the king
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_column)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_column)
        # swap players after move
        self.white_to_move = not self.white_to_move

        # if pawn promotion, we automatically promote to a queen
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + 'Q'

        # en passant case
        if move.is_enpassant_move:
            # capturing the pawn
            self.board[move.start_row][move.end_column] = '--'

        # update enpassant_possible variable
        # only on 2 square pawn advances
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_column)
        else:
            self.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            # king side castle
            if move.end_column - move.start_column == 2:
                # put the rook in the new square
                self.board[move.end_row][move.end_column - 1] = self.board[move.end_row][move.end_column + 1]
                # delete old rook position
                self.board[move.end_row][move.end_column + 1] = '--'
            # queen side castle
            else:
                # put the rook in the new square
                self.board[move.end_row][move.end_column + 1] = self.board[move.end_row][move.end_column - 2]
                # delete old rook position
                self.board[move.end_row][move.end_column - 2] = '--'

        # update castling rights
        # update rights on rook and king moves
        self.update_castling_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.white_king_side,
                                                   self.current_castling_rights.black_king_side,
                                                   self.current_castling_rights.white_queen_side,
                                                   self.current_castling_rights.black_queen_side))

    """
    function that does undo on last move
    """

    def undo_move(self):
        # check if there is a move to undo
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.piece_moved
            self.board[move.end_row][move.end_column] = move.piece_captured
            # update the location of the king
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_column)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_column)
            self.white_to_move = not self.white_to_move
            # undo en passant
            if move.is_enpassant_move:
                # leave landing square blank
                self.board[move.end_row][move.end_column] = '--'
                # restore opponent piece
                self.board[move.start_row][move.end_column] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_column)
            # undo 2 square pawn advance
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()

            # undo castling rights - getting back to previous castling rights
            self.castle_rights_log.pop()
            self.current_castling_rights = self.castle_rights_log[-1]

            # undo castling move
            if move.is_castle_move:
                # king side castle
                if move.end_column - move.start_column == 2:
                    self.board[move.end_row][move.end_column + 1] = self.board[move.end_row][move.end_column - 1]
                    self.board[move.end_row][move.end_column - 1] = '--'
                # queen side castle
                else:
                    self.board[move.end_row][move.end_column - 2] = self.board[move.end_row][move.end_column + 1]
                    self.board[move.end_row][move.end_column + 1] = '--'

            self.checkmate = False
            self.stalemate = False

    """
    update castle rights given the move
    """

    def update_castling_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_rights.white_king_side = False
            self.current_castling_rights.white_queen_side = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.black_king_side = False
            self.current_castling_rights.black_queen_side = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                # left rook
                if move.start_column == 0:
                    self.current_castling_rights.white_queen_side = False
                # right rook
                elif move.start_column == 7:
                    self.current_castling_rights.white_king_side = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                # left rook
                if move.start_column == 0:
                    self.current_castling_rights.black_queen_side = False
                # right rook
                elif move.start_column == 7:
                    self.current_castling_rights.black_king_side = False

        # if a rook is captured, cancel castle rights
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_column == 0:
                    self.current_castling_rights.white_queen_side = False
                elif move.end_column == 7:
                    self.current_castling_rights.white_king_side = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_column == 0:
                    self.current_castling_rights.black_queen_side = False
                elif move.end_column == 7:
                    self.current_castling_rights.black_king_side = False

    """
    get all moves for one side also considering checks
    """

    def get_valid_moves(self):
        moves = []
        self.is_king_in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_column = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_column = self.black_king_location[1]
        # king is in check
        if self.is_king_in_check:
            # only 1 check, not a double one
            # 2 choices : block the check or move the king
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                # getting information from the checking square and piece
                check = self.checks[0]
                check_row = check[0]
                check_column = check[1]
                # getting the piece that checks the king
                piece_checking = self.board[check_row][check_column]
                # create array of valid squares we can move to in order to evade check
                valid_squares_to_move_to = []
                # if knight check => capture knight or move king
                if piece_checking[1] == 'N':
                    valid_squares_to_move_to = [(check_row, check_column)]
                else:
                    for shift in range(1, 8):
                        # check[2], check[3] = directions
                        valid_square = (king_row + check[2] * shift, king_column + check[3] * shift)
                        valid_squares_to_move_to.append(valid_square)
                        # we got to the checking piece => end check
                        if valid_square[0] == check_row and valid_square[1] == check_column:
                            break
                # iterate through possible moves and remove those who don't block the check or move the king away
                # from check
                for index in range(len(moves) - 1, -1, -1):
                    # it must be a block or capture because king is not moved
                    if moves[index].piece_moved[1] != 'K':
                        # move does not block check or capture checking piece
                        if not (moves[index].end_row, moves[index].end_column) in valid_squares_to_move_to:
                            moves.remove(moves[index])
            # double check so we must move - no other option
            else:
                self.get_king_moves(king_row, king_column, moves)
        # king not in check so all is fine
        else:
            moves = self.get_all_possible_moves()
            self.get_castle_moves(king_row, king_column, moves)

        if len(moves) == 0:
            if self.is_king_in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.stalemate = False
            self.checkmate = False

        return moves

    """
    determine if current player is in check
    """

    def king_in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    """
    determine if opponent can attack square on given row and column
    """

    def square_under_attack(self, row, column):
        # switch point of view to opponent view
        self.white_to_move = not self.white_to_move
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponent_moves:
            if move.end_row == row and move.end_column == column:
                return True
        return False

    """
    get all moves for one side, but checks are not considered
    """

    def get_all_possible_moves(self):
        moves = []
        # iterate through all squares
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][column][1]
                    # call the corresponding move functions
                    self.move_functions[piece](row, column, moves)
        return moves

    """
    checking for pinned pieces and current checks applied to the king
    """

    def check_for_pins_and_checks(self):
        # squares where pinned pieces from same side are + the direction of the pin
        pins = []
        # squares from where enemy pieces are checking
        checks = []
        is_king_in_check = False

        # start from the king for pins and checks
        if self.white_to_move:
            enemy_colour = "b"
            ally_colour = "w"
            start_row = self.white_king_location[0]
            start_column = self.white_king_location[1]
        else:
            enemy_colour = "w"
            ally_colour = "b"
            start_row = self.black_king_location[0]
            start_column = self.black_king_location[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for index in range(len(directions)):
            direction = directions[index]
            # reset possible pins
            possible_pin = ()
            for shift in range(1, 8):
                end_row = start_row + direction[0] * shift
                end_column = start_column + direction[1] * shift
                # check if it is a valid square
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    end_piece = self.board[end_row][end_column]
                    if end_piece[0] == ally_colour and end_piece[1] != 'K':
                        # first allied piece could be pinned
                        if possible_pin == ():
                            possible_pin = (end_row, end_column, direction[0], direction[1])
                        # this is not first allied piece on this direction => no pin or check is possible
                        else:
                            break
                    elif end_piece[0] == enemy_colour:
                        piece_type = end_piece[1]
                        # 5 possibilities of pinning
                        #   a) rook pin on files or ranks
                        #   b) bishop pin on diagonal
                        #   c) pawn pin (1 square away on diagonals)
                        #   d) queen pin on any direction
                        #   e) king pin (2 kings cannot be on 2 next to each other squares)
                        if (0 <= index <= 3 and piece_type == 'R') or \
                                (4 <= index <= 7 and piece_type == 'B') or \
                                (shift == 1 and piece_type == 'p' and ((enemy_colour == 'w' and 6 <= index <= 7) or (
                                        enemy_colour == 'b' and 4 <= index <= 5))) or \
                                (piece_type == 'Q') or (shift == 1 and type == 'K'):
                            # no blocking piece => check
                            if possible_pin == ():
                                is_king_in_check = True
                                checks.append((end_row, end_column, direction[0], direction[1]))
                                break
                            # there is a blocking piece => pin
                            else:
                                pins.append(possible_pin)
                                break
                        # enemy piece not applying check
                        else:
                            break
        # now we take care of knight pins and checks - we treat them separately because they move in a special way
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_column = start_column + move[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                # check if enemy knight attacks king
                if end_piece[0] == enemy_colour and end_piece[1] == 'N':
                    is_king_in_check = True
                    checks.append((end_row, end_column, move[0], move[1]))
        return is_king_in_check, pins, checks

    """
    get all pawn moves for pawn located at row and column given and add possible moves to move array 
    """

    def get_pawn_moves(self, row, column, moves):

        piece_pinned = False
        pin_direction = ()
        # first we check if the piece we want to move is pinned
        for index in range(len(self.pins) - 1, -1, -1):
            if self.pins[index][0] == row and self.pins[index][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[index][2], self.pins[index][3])
                self.pins.remove(self.pins[index])
                break

        # focus on white pawns
        if self.white_to_move:
            # one square ahead is empty
            if self.board[row - 1][column] == "--":
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, column), (row - 1, column), self.board))
                    # check if a 2 square move ahead is possible for pawn
                    if row == 6 and self.board[row - 2][column] == "--":
                        moves.append(Move((row, column), (row - 2, column), self.board))
            # check for capture moves from pawns (left captures)
            if column - 1 >= 0:
                # there is an opponent piece to capture
                if self.board[row - 1][column - 1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, column), (row - 1, column - 1), self.board))
                elif (row - 1, column - 1) == self.enpassant_possible:
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, column), (row - 1, column - 1), self.board, is_enpassant_move=True))
            # check for capture moves from pawns (right captures)
            if column + 1 <= 7:
                if self.board[row - 1][column + 1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, column), (row - 1, column + 1), self.board))
                elif (row - 1, column + 1) == self.enpassant_possible:
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, column), (row - 1, column + 1), self.board, is_enpassant_move=True))
        # focus on black pawns
        else:
            # one square ahead is empty
            if self.board[row + 1][column] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, column), (row + 1, column), self.board))
                    # check if a 2 square move ahead is possible for pawn
                    if row == 1 and self.board[row + 2][column] == "--":
                        moves.append(Move((row, column), (row + 2, column), self.board))
            # check for capture moves from pawns (left captures)
            if column - 1 >= 0:
                # there is an opponent piece to capture
                if self.board[row + 1][column - 1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, column), (row + 1, column - 1), self.board))
                elif (row + 1, column - 1) == self.enpassant_possible:
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, column), (row + 1, column - 1), self.board, is_enpassant_move=True))
            # check for capture moves from pawns (right captures)
            if column + 1 <= 7:
                if self.board[row + 1][column + 1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, column), (row + 1, column + 1), self.board))
                elif (row + 1, column + 1) == self.enpassant_possible:
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, column), (row + 1, column + 1), self.board, is_enpassant_move=True))

    """
    get all rook moves for rooks located at row and column given and add possible moves to move array
    """

    def get_rook_moves(self, row, column, moves):

        piece_pinned = False
        pin_direction = ()
        # first we check if the piece we want to move is pinned
        for index in range(len(self.pins) - 1, -1, -1):
            if self.pins[index][0] == row and self.pins[index][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[index][2], self.pins[index][3])
                # cannot remove queen from pin on rook moves, only on bishop moves
                if self.board[row][column][1] != 'Q':
                    self.pins.remove(self.pins[index])
                break

        # up, left, down, right directions
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        # opponent colour
        enemy_colour = "b" if self.white_to_move else "w"
        for direction in directions:
            for value in range(1, 8):
                end_row = row + direction[0] * value
                end_column = column + direction[1] * value
                # we are still on board
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_column]
                        # there is not a capture, but just a simple rook move
                        if end_piece == "--":
                            moves.append(Move((row, column), (end_row, end_column), self.board))
                        # there is an opponent piece on that square
                        elif end_piece[0] == enemy_colour:
                            moves.append(Move((row, column), (end_row, end_column), self.board))
                            # no point to check farther squares, we have stumbled into a piece already
                            break
                        # there is a playing side's piece on that square
                        else:
                            break
                # we are not anymore on the board
                else:
                    break

    """
    get all knight moves for knights located at row and column given and add possible moves to move array
    """

    def get_knight_moves(self, row, column, moves):

        piece_pinned = False
        # first we check if the piece we want to move is pinned
        for index in range(len(self.pins) - 1, -1, -1):
            if self.pins[index][0] == row and self.pins[index][1] == column:
                piece_pinned = True
                self.pins.remove(self.pins[index])
                break

        knight_directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        # same side colour
        friend_colour = "w" if self.white_to_move else "b"
        for direction in knight_directions:
            end_row = row + direction[0]
            end_column = column + direction[1]
            # we are still on board
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_column]
                    # valid knight move
                    if end_piece[0] != friend_colour:
                        moves.append(Move((row, column), (end_row, end_column), self.board))

    """
    get all bishop moves for bishops located at row and column given and add possible moves to move array
    """

    def get_bishop_moves(self, row, column, moves):

        piece_pinned = False
        pin_direction = ()
        # first we check if the piece we want to move is pinned
        for index in range(len(self.pins) - 1, -1, -1):
            if self.pins[index][0] == row and self.pins[index][1] == column:
                piece_pinned = True
                pin_direction = (self.pins[index][2], self.pins[index][3])
                self.pins.remove(self.pins[index])
                break

        # top-left, top-right, bottom-left, bottom-right directions
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        # opponent colour
        enemy_colour = "b" if self.white_to_move else "w"
        for direction in directions:
            for value in range(1, 8):
                end_row = row + direction[0] * value
                end_column = column + direction[1] * value
                # we are still on board
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_column]
                        # there is not a capture, but just a simple bishop move
                        if end_piece == "--":
                            moves.append(Move((row, column), (end_row, end_column), self.board))
                        # there is an opponent piece on that square
                        elif end_piece[0] == enemy_colour:
                            moves.append(Move((row, column), (end_row, end_column), self.board))
                            # no point to check farther squares, we have stumbled into a piece already
                            break
                        # there is a playing side's piece on that square
                        else:
                            break
                # we are not anymore on the board
                else:
                    break

    """
    get all queen moves for queens located at row and column given and add possible moves to move array
    """

    def get_queen_moves(self, row, column, moves):
        self.get_rook_moves(row, column, moves)
        self.get_bishop_moves(row, column, moves)

    """
    get all king moves for kings located at row and column given and add possible moves to move array
    """

    def get_king_moves(self, row, column, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        column_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_colour = "w" if self.white_to_move else "b"
        for index in range(8):
            end_row = row + row_moves[index]
            end_column = column + column_moves[index]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_piece = self.board[end_row][end_column]
                # not an allied piece
                if end_piece[0] != ally_colour:
                    # place king on end square and check for checks
                    # basically, we temporarily make the move to see if we are in check, and then we undo the move
                    if ally_colour == "w":
                        self.white_king_location = (end_row, end_column)
                    else:
                        self.black_king_location = (end_row, end_column)
                    king_in_check, pins, checks = self.check_for_pins_and_checks()
                    if not king_in_check:
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                    # place king back on initial square
                    if ally_colour == "w":
                        self.white_king_location = (row, column)
                    else:
                        self.black_king_location = (row, column)

    """
    generate all valid castle moves for the king at row and column given + add them to the list of moves
    """

    def get_castle_moves(self, row, column, moves):
        # cannot castle while king in check
        if self.square_under_attack(row, column):
            return
        if (self.white_to_move and self.current_castling_rights.white_king_side) or \
                (not self.white_to_move and self.current_castling_rights.black_king_side):
            self.get_king_side_castle_moves(row, column, moves)
        if (self.white_to_move and self.current_castling_rights.white_queen_side) or \
                (not self.white_to_move and self.current_castling_rights.black_queen_side):
            self.get_queen_side_castle_moves(row, column, moves)

    """
    generate king side castle moves for the king at (row, column)
    method called only if player still has castle rights king side
    """
    def get_king_side_castle_moves(self, row, column, moves):
        if self.board[row][column + 1] == '--' and self.board[row][column + 2] == '--':
            if not self.square_under_attack(row, column + 1) and not self.square_under_attack(row, column + 2):
                moves.append(Move((row, column), (row, column + 2), self.board, is_castle_move=True))

    """
    generate queen side castle moves for the king at (row, column)
    method called only if player still has castle rights queen side
    """
    def get_queen_side_castle_moves(self, row, column, moves):
        if self.board[row][column - 1] == '--' and self.board[row][column - 2] == '--' \
                and self.board[row][column - 3] == '--':
            if not self.square_under_attack(row, column - 1) and not self.square_under_attack(row, column - 2):
                moves.append(Move((row, column), (row, column - 2), self.board, is_castle_move=True))


class Move:
    rank_to_row = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0,
    }
    row_to_rank = {
        value: key for key, value in rank_to_row.items()
    }
    file_to_column = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7
    }
    column_to_file = {
        value: key for key, value in file_to_column.items()
    }

    def __init__(self, start_square, end_square, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_square[0]
        self.start_column = start_square[1]
        self.end_row = end_square[0]
        self.end_column = end_square[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        # check if move is a pawn promotion
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or \
                                 (self.piece_moved == 'bp' and self.end_row == 7)
        # check if en passant move
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'
        # castle move
        self.is_castle_move = is_castle_move
        self.move_id = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column

    """
    override equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        # chess notations for the moves we make
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.column_to_file[column] + self.row_to_rank[row]


"""
class that handles the castling rights of a side at any point of the game
"""


class CastleRights:
    def __init__(self, white_king_side, black_king_side, white_queen_side, black_queen_side):
        self.white_king_side = white_king_side
        self.white_queen_side = white_queen_side
        self.black_king_side = black_king_side
        self.black_queen_side = black_queen_side
