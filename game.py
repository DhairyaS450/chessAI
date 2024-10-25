import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800  # Screen dimensions
ROWS, COLS = 8, 8         # Chessboard dimensions
SQUARE_SIZE = WIDTH // COLS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
SELECTED_COLOR = (255, 0, 0)  # Highlight selected square in red
PIECE_IMAGES = {}

# Load piece images
def load_images():
    pieces = ['R', 'N', 'B', 'Q', 'K', 'P', 'r', 'n', 'b', 'q', 'k', 'p']
    for piece in pieces:
        PIECE_IMAGES[piece] = pygame.transform.scale(pygame.image.load(f'images/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))

# Draw the chessboard
def draw_board(screen, selected_square):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else GREEN
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Highlight selected square
            if selected_square == (row, col):
                pygame.draw.rect(screen, SELECTED_COLOR, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

# Draw the pieces on the board
def draw_pieces(screen, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != '-':
                screen.blit(PIECE_IMAGES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Initialize the chessboard
def initialize_board():
    return [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['-', '-', '-', '-', '-', '-', '-', '-'],
        ['-', '-', '-', '-', '-', '-', '-', '-'],
        ['-', '-', '-', '-', '-', '-', '-', '-'],
        ['-', '-', '-', '-', '-', '-', '-', '-'],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]

# Get mouse position on the board
def get_square_under_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

# Move validation: Only basic movement validation for pawns, rooks, knights, bishops, queens, kings
def validate_move(board, piece, start_pos, end_pos, turn):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    # Get the piece at the start and end positions
    start_piece = board[start_row][start_col]
    end_piece = board[end_row][end_col]

    # Prevent moving empty spaces or opponent's turn
    if start_piece == '-':
        return False
    if (turn == 'white' and start_piece.islower()) or (turn == 'black' and start_piece.isupper()):
        return False

    # Prevent capturing own pieces
    if (turn == 'white' and end_piece.isupper()) or (turn == 'black' and end_piece.islower()):
        return False

    piece = piece.lower()
    
    # Pawn movement
    if piece == 'p':
        direction = -1 if start_piece.isupper() else 1  # White moves up, black moves down
        if start_col == end_col and board[end_row][end_col] == '-':
            # Regular pawn move
            if end_row == start_row + direction:
                return True
            # Initial double move
            if (start_row == 1 or start_row == 6) and end_row == start_row + 2 * direction and board[start_row + direction][start_col] == '-':
                return True
        # Pawn capture
        elif abs(start_col - end_col) == 1 and end_row == start_row + direction and end_piece != '-':
            return True

    # Rook movement
    if piece == 'r':
        if start_row == end_row or start_col == end_col:  # Move in straight lines
            if clear_path(board, start_pos, end_pos):
                return True

    # Knight movement
    if piece == 'n':
        if (abs(start_row - end_row) == 2 and abs(start_col - end_col) == 1) or \
           (abs(start_row - end_row) == 1 and abs(start_col - end_col) == 2):
            return True

    # Bishop movement
    if piece == 'b':
        if abs(start_row - end_row) == abs(start_col - end_col):  # Move diagonally
            if clear_path(board, start_pos, end_pos):
                return True

    # Queen movement
    if piece == 'q':
        if (start_row == end_row or start_col == end_col) or \
           (abs(start_row - end_row) == abs(start_col - end_col)):
            if clear_path(board, start_pos, end_pos):
                return True

    # King movement
    if piece == 'k':
        if abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1:
            return True

    return False

# Helper function to check if path between two squares is clear (for rooks, bishops, queens)
def clear_path(board, start, end):
    start_row, start_col = start
    end_row, end_col = end

    if start_row == end_row:
        step = 1 if start_col < end_col else -1
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] != '-':
                return False
    elif start_col == end_col:
        step = 1 if start_row < end_row else -1
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] != '-':
                return False
    else:
        row_step = 1 if start_row < end_row else -1
        col_step = 1 if start_col < end_col else -1
        for i in range(1, abs(start_row - end_row)):
            if board[start_row + i * row_step][start_col + i * col_step] != '-':
                return False

    return True

# Check if the move puts the king in check
def check_check(board, king_pos, turn):
    """
    Checks if the current player's king is in check.
    :param board: The chessboard.
    :param king_pos: The position (row, col) of the current player's king.
    :param turn: The current player's turn ('white' or 'black').
    :return: True if the king is in check, False otherwise.
    """
    enemy_turn = 'black' if turn == 'white' else 'white'
    
    # Loop through the entire board and check if any enemy piece can attack the king
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if (enemy_turn == 'white' and piece.isupper()) or (enemy_turn == 'black' and piece.islower()):
                if validate_move(board, piece, (row, col), king_pos, enemy_turn):
                    return True  # King is in check
    return False  # King is not in check

# Check position for checkmate
def check_checkmate(board, king_pos, turn):
    """
    Checks if the current player's king is in checkmate.
    :param board: The chessboard.
    :param king_pos: The position (row, col) of the current player's king.
    :param turn: The current player's turn ('white' or 'black').
    :return: True if the king is in checkmate, False otherwise.
    """
    if not check_check(board, king_pos, turn):
        return False  # King is not in check, so no checkmate

    # Generate all possible moves for the current player
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if (turn == 'white' and piece.isupper()) or (turn == 'black' and piece.islower()):
                for r in range(ROWS):
                    for c in range(COLS):
                        # Test if the move is valid and would result in escaping check
                        if validate_move(board, piece, (row, col), (r, c), turn):
                            # Temporarily move the piece
                            temp_board = [row.copy() for row in board]  # Create a temporary copy of the board
                            move_piece(temp_board, (row, col), (r, c))
                            
                            # Check if the king is still in check after the move
                            if not check_check(temp_board, king_pos, turn):
                                return False  # There's a move that can prevent checkmate

    return True  # No valid moves left, checkmate

# Check position for stalemate
def check_stalemate(board, turn):
    """
    Checks if the current player is in stalemate.
    :param board: The chessboard.
    :param turn: The current player's turn ('white' or 'black').
    :return: True if the player is in stalemate, False otherwise.
    """
    # Loop through all pieces of the current player
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if (turn == 'white' and piece.isupper()) or (turn == 'black' and piece.islower()):
                # Try all possible moves for the current player
                for r in range(ROWS):
                    for c in range(COLS):
                        if validate_move(board, piece, (row, col), (r, c), turn):
                            # If there's at least one valid move, it's not stalemate
                            temp_board = [row.copy() for row in board]  # Create a temporary copy of the board
                            move_piece(temp_board, (row, col), (r, c))
                            
                            # Check if this move doesn't result in check
                            king_pos = find_king(board, turn)  # You need to implement find_king() to locate the king
                            if not check_check(temp_board, king_pos, turn):
                                return False  # Not stalemate, a valid move exists

    return True  # No valid moves and king is not in check, it's a stalemate

# Helper function: find the king's position
def find_king(board, turn):
    """
    Find the king's position on the board.
    :param board: The chessboard.
    :param turn: The current player's turn ('white' or 'black').
    :return: The position (row, col) of the current player's king.
    """
    king_symbol = 'K' if turn == 'white' else 'k'
    
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == king_symbol:
                return (row, col)
    return None  # King not found (shouldn't happen in a valid game)

# Move pieces
def move_piece(board, start, end):
    piece = board[start[0]][start[1]]
    board[start[0]][start[1]] = '-'
    board[end[0]][end[1]] = piece
    
# Main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    board = initialize_board()
    load_images()

    selected_square = None  # Square selected by the player
    turn = 'white'  # Track turns: white moves first
    running = True
    clock = pygame.time.Clock()

    while running:
        draw_board(screen, selected_square)
        draw_pieces(screen, board)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_square_under_mouse(pos)

                if selected_square:
                    # Validate move before applying it
                    start_row, start_col = selected_square
                    if validate_move(board, board[start_row][start_col], selected_square, (row, col), turn):
                        move_piece(board, selected_square, (row, col))

                        # Check if the move puts the opponent's king in check or leads to checkmate/stalemate
                        opponent_turn = 'black' if turn == 'white' else 'white'
                        king_pos = find_king(board, opponent_turn)  # Find opponent's king position

                        # Check for checkmate and stalemate after the move
                        if check_checkmate(board, king_pos, opponent_turn):
                            print(f"Checkmate! {turn.capitalize()} wins.")
                            running = False  # End the game
                        elif check_stalemate(board, opponent_turn):
                            print("Stalemate! It's a draw.")
                            running = False  # End the game
                        elif check_check(board, king_pos, opponent_turn):
                            print(f"{opponent_turn.capitalize()} is in check.")

                        # Switch turns after a valid move
                        turn = 'black' if turn == 'white' else 'white'

                    selected_square = None  # Reset selection after move
                else:
                    selected_square = (row, col)

        clock.tick(60)

main()