"""
main file for this project
responsible for user input handling and also displays the current GameState object
"""

import pygame as p
from Chess import engine, aiMoveFinder
from multiprocessing import Process, Queue

# width and height of the board
BOARD_WIDTH = BOARD_HEIGHT = 512
# width and height for the move log panel
MOVE_LOG_PANEL_WIDTH = 300
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
# standard number of rows and columns
DIMENSION = 8
# the dimension of a square determined by height and number of rows/columns
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
# animations fps
MAXIMUM_FPS = 15
# dictionary of images for pieces
IMAGES = {}

global colours
global return_queue

"""
Initialize a global dictionary of images (called only once in main)
each piece has its own image from the images directory in order to build the board
images are accessible by using the dictionary
"""


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    # using python transform.scale to scale the dimensions of the imported images to the dimensions we want
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


"""
main function
user input handled + graphics update
"""


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 20, False, False)
    game_state = engine.GameState()
    valid_moves = game_state.get_valid_moves()
    # flag variable for when a move is made
    move_made = False
    # flag for when we should animate a move
    animate = False
    load_images()
    is_program_running = True
    # initially , no square is selected
    # tuple format (row, column)
    selected_square = ()
    # tracker of player clicks
    # click = 2 tuples: [(6, 4), (4, 4)]
    player_clicks = []
    game_over = False
    # if human plays white, variable is true; if AI is playing, than false
    player_one = True
    # if human plays black, variable is true; if AI is playing, than false
    player_two = False
    # used for threading and responsiveness while AI thinks
    ai_thinking = False
    move_finder_process = None
    move_undone = False
    while is_program_running:
        is_human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        for event in p.event.get():
            if event.type == p.QUIT:
                is_program_running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    # coordinates of mouse position
                    location = p.mouse.get_pos()
                    mouse_column = location[0] // SQUARE_SIZE
                    mouse_row = location[1] // SQUARE_SIZE
                    # user clicks same square twice or user clicked move log => undo selection
                    if selected_square == (mouse_row, mouse_column) or mouse_column >= 8:
                        # deselect and reset clicks
                        selected_square = ()
                        player_clicks = []
                    else:
                        selected_square = (mouse_row, mouse_column)
                        player_clicks.append(selected_square)
                    # check if it was user second click
                    if len(player_clicks) == 2 and is_human_turn:
                        move = engine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                # reset user clicks
                                selected_square = ()
                                player_clicks = []
                        # invalid move tried
                        if not move_made:
                            player_clicks = [selected_square]
            # undo move when pressing z key
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    move_made, animate, ai_thinking, move_undone, game_over = \
                        handle_undo_move(game_state, move_finder_process, ai_thinking)
                # reset the board on r key
                if event.key == p.K_r:
                    game_state, valid_moves, selected_square, player_clicks, move_made, animate, ai_thinking, \
                        move_undone, game_over = handle_restart_game(move_finder_process, ai_thinking)

        # AI finder - finder of moves
        if not game_over and not is_human_turn and not move_undone:
            if not ai_thinking:
                # engine starts thinking about new move
                move_finder_process, ai_thinking = engine_starts_thinking(game_state, valid_moves)

            # engine is done thinking, so we take the move from the queue, and we make the move
            if not move_finder_process.is_alive():
                ai_move, ai_thinking, move_made, animate = make_move_after_ai_thinking(game_state, valid_moves)

        # animate last move and get next valid moves
        if move_made:
            valid_moves, move_made, animate, move_undone = animate_move_and_get_next_valid_moves(game_state,
                                                                                                 screen, clock, animate)

        draw_game_state(screen, game_state, valid_moves, selected_square, move_log_font)
        # print message if checkmate or stalemate
        game_over = print_message_if_checkmate_or_stalemate(game_state, screen, game_over)

        clock.tick(MAXIMUM_FPS)
        p.display.flip()


"""
method that makes the move after ai finishes thinking
"""


def make_move_after_ai_thinking(game_state, valid_moves):
    print("done thinking!")
    ai_thinking = False
    ai_move = return_queue.get()
    if ai_move is None:
        ai_move = aiMoveFinder.find_random_move(valid_moves)
    game_state.make_move(ai_move)
    move_made = True
    animate = True
    return ai_move, ai_thinking, move_made, animate


"""
method that gets the engine to start thinking about a new move given the current state and valid moves
another thread is used for this task
"""


def engine_starts_thinking(game_state, valid_moves):
    global return_queue
    ai_thinking = True
    print("thinking ...")
    # queue used to pass data between threads
    return_queue = Queue()
    move_finder_process = Process(target=aiMoveFinder.find_best_move, args=(game_state, valid_moves,
                                                                            return_queue))
    # call method to find best move from AI
    move_finder_process.start()
    return move_finder_process, ai_thinking


"""
method that animates last move and sets some boolean to False
also, next valid moves are generated 
"""


def animate_move_and_get_next_valid_moves(game_state, screen, clock, animate):
    if animate:
        animate_move(game_state.move_log[-1], screen, game_state.board, clock)
    valid_moves = game_state.get_valid_moves()
    move_made = False
    animate = False
    move_undone = False
    return valid_moves, move_made, animate, move_undone


"""
method that handles the event created by pressing z keyboard which means undo
"""


def handle_undo_move(game_state, move_finder_process, ai_thinking):
    game_state.undo_move()
    move_made = True
    animate = False
    game_over = False
    if ai_thinking:
        move_finder_process.terminate()
        ai_thinking = False
    move_undone = True
    return move_made, animate, ai_thinking, move_undone, game_over


"""
method that handles the event created by pressing r keyboard which means game reset
"""


def handle_restart_game(move_finder_process, ai_thinking):
    game_state = engine.GameState()
    valid_moves = game_state.get_valid_moves()
    selected_square = ()
    player_clicks = []
    move_made = False
    animate = False
    game_over = False
    if ai_thinking:
        move_finder_process.terminate()
        ai_thinking = False
    move_undone = True
    return game_state, valid_moves, selected_square, player_clicks, move_made, animate, ai_thinking, move_undone, \
        game_over


"""
method that prints a message at the end of the game if stalemate or checkmate
"""


def print_message_if_checkmate_or_stalemate(game_state, screen, game_over):
    if game_state.checkmate or game_state.stalemate:
        game_over = True
        text = 'Stalemate' if game_state.stalemate else 'Black wins by checkmate' if game_state.white_to_move else \
            'White wins by checkmate'
        draw_endgame_text(screen, text)
    return game_over


"""
responsible for all design and graphics within the current state of the game
"""


def draw_game_state(screen, game_state, valid_moves, square_selected, move_log_font):
    draw_board(screen)
    highlight_squares(screen, game_state, valid_moves, square_selected)
    draw_pieces(screen, game_state.board)
    draw_move_log(screen, game_state, move_log_font)


"""
draw the squares on the board
typically white and gray squares
top left square is white
"""


def draw_board(screen):
    global colours
    colours = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            # light squares are those where the sum of row and column is an even number
            # dark squares are those where the sum and column is an odd number
            colour = colours[(row + column) % 2]
            p.draw.rect(screen, colour, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


"""
highlight square selected and valid moves for piece selected
"""


def highlight_squares(screen, game_state, valid_moves, square_selected):
    if square_selected != ():
        row, column = square_selected
        # make sure that square selected is a piece that can be moved
        if game_state.board[row][column][0] == ('w' if game_state.white_to_move else 'b'):
            # highlight selected square
            surface = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            # transparency value
            surface.set_alpha(100)
            surface.fill(p.Color('blue'))
            screen.blit(surface, (column * SQUARE_SIZE, row * SQUARE_SIZE))
            # highlight moves from selected square
            surface.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_column == column:
                    screen.blit(surface, (SQUARE_SIZE * move.end_column, SQUARE_SIZE * move.end_row))


"""
draw the pieces on the board
it takes under consideration the current state of the game - board attribute of the GameState
"""


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            # check if square is empty or not
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


"""
methods that draws the move log - list with all played moves
"""


def draw_move_log(screen, game_state, font):
    move_log_rectangle = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), move_log_rectangle)
    move_log = game_state.move_log
    move_texts = []
    for index in range(0, len(move_log), 2):
        move_string = str(index // 2 + 1) + ". " + str(move_log[index]) + " "
        # make sure black made a move
        if index + 1 < len(move_log):
            move_string += str(move_log[index + 1]) + " "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    text_y = padding
    line_spacing = 2
    # try to print 3 moves on a row
    for index in range(0, len(move_texts), moves_per_row):
        text = ""
        for second_index in range(moves_per_row):
            if index + second_index < len(move_texts):
                text += move_texts[index + second_index]
        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rectangle.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


"""
animating move function
"""


def animate_move(move, screen, board, clock):
    global colours
    # list of coordinates the animation will move through
    row_difference = move.end_row - move.start_row
    column_difference = move.end_column - move.start_column
    # frames to move one square
    frames_per_square = 10
    frame_count = (abs(row_difference) + abs(column_difference)) * frames_per_square
    for frame in range(frame_count + 1):
        # a series of coordinates from start position to end position used for animation
        row, column = (move.start_row + row_difference * frame / frame_count,
                       move.start_column + column_difference * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from ending square
        colour = colours[(move.end_row + move.end_column) % 2]
        end_square = p.Rect(move.end_column * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, colour, end_square)
        # draw captured piece into the rectangle
        if move.piece_captured != '--':
            # special animation for enpassant
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_column * SQUARE_SIZE,
                                    enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw the moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        # 60 frames per animation
        clock.tick(60)


"""
method that writes the text at the end of the game
text could be stalemate or checkmate depending on the result of the game
"""


def draw_endgame_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color('Gray'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color("Black"))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    main()
