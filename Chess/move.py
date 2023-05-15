

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

        self.is_capture = self.piece_captured != '--'
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

    def __str__(self):
        # castle move
        if self.is_castle_move:
            return "O-O" if self.end_column == 6 else "O-O-O"
        end_square = self.get_rank_file(self.end_row, self.end_column)
        # pawn move
        if self.piece_moved[1] == 'p':
            if self.is_capture:
                return self.column_to_file[self.start_column] + "x" + end_square
            else:
                return end_square
            # pawn promotion
        # two of same type of pieces moving to a square - Nbd2
        # check and checkmate move

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += 'x'
        return move_string + end_square
