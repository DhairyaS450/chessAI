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

# Variables for Castling
white_king_moved = False
black_king_moved = False
white_rook_king_side_moved = False
white_rook_queen_side_moved = False
black_rook_king_side_moved = False
black_rook_queen_side_moved = False

en_passant_square = None  # Set to (row, col) when en passant is available

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

    # Simulate the move to test for check
    original_start_piece = board[start_row][start_col]
    original_end_piece = board[end_row][end_col]

    board[start_row][start_col] = '-' # Temporarily clear the starting square
    board[end_row][end_col] = start_piece # Place the piece at the new position

    # Check if the move results in check for the player's own king
    if check_check(board, turn):
        # Revert the board to the original position
        board[start_row][start_col] = original_start_piece
        board[end_row][end_col] = original_end_piece
        return False # Move is invalid as it places the king in check
    
    # Revert the board for rest of validations
    board[start_row][start_col] = original_start_piece
    board[end_row][end_col] = original_end_piece

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
        elif abs(start_col - end_col) == 1:
            if end_row == start_row + direction:
                # Regular capture
                if end_piece != '-':
                    return True
                # En passant capture
                elif en_passant_square == (end_row, end_col):
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

def check_check(board, turn):
    # Locate the current player's king
    king = 'K' if turn == 'white' else 'k'
    king_pos = None
    
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == king:
                king_pos = (row, col)
                break
        if king_pos:
            break

    if not king_pos:
        raise ValueError("King not found on the board")  # Safety check

    # Check all opposing pieces to see if any can capture the king
    opponent_turn = 'black' if turn == 'white' else 'white'
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            
            # Skip empty squares or current player's pieces
            if piece == '-' or (turn == 'white' and piece.isupper()) or (turn == 'black' and piece.islower()):
                continue
            
            # Determine if this piece can move to the king's position
            start_pos = (row, col)
            if is_threatening_king(board, piece, start_pos, king_pos):
                return True  # King is in check

    return False  # No threats to the king

def is_threatening_king(board, piece, start_pos, king_pos):
    """ Helper function to check if a piece at start_pos can capture the king at king_pos. """
    start_row, start_col = start_pos
    end_row, end_col = king_pos
    piece = piece.lower()

    # Pawn movement (checks capture only)
    if piece == 'p':
        direction = -1 if board[start_row][start_col].isupper() else 1
        if abs(start_col - end_col) == 1 and end_row == start_row + direction:
            return True

    # Rook movement (straight line)
    elif piece == 'r' and (start_row == end_row or start_col == end_col):
        if clear_path(board, start_pos, king_pos):
            return True

    # Knight movement (L-shape)
    elif piece == 'n':
        if (abs(start_row - end_row) == 2 and abs(start_col - end_col) == 1) or \
           (abs(start_row - end_row) == 1 and abs(start_col - end_col) == 2):
            return True

    # Bishop movement (diagonal)
    elif piece == 'b' and abs(start_row - end_row) == abs(start_col - end_col):
        if clear_path(board, start_pos, king_pos):
            return True

    # Queen movement (combination of rook and bishop)
    elif piece == 'q':
        if (start_row == end_row or start_col == end_col or
            abs(start_row - end_row) == abs(start_col - end_col)):
            if clear_path(board, start_pos, king_pos):
                return True

    # King movement (one square in any direction)
    elif piece == 'k':
        if abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1:
            return True

    return False

def is_checkmate(board, turn):
    if not check_check(board, turn):
        return False  # Not in check, so cannot be checkmate

    # Check if any legal move can escape check
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if (turn == 'white' and piece.isupper()) or (turn == 'black' and piece.islower()):
                start_pos = (row, col)
                
                # Try moving the piece to all squares on the board
                for end_row in range(ROWS):
                    for end_col in range(COLS):
                        end_pos = (end_row, end_col)
                        
                        # Check if the move is valid and doesn't leave the king in check
                        if validate_move(board, piece, start_pos, end_pos, turn):
                            # Temporarily make the move
                            original_start = board[start_pos[0]][start_pos[1]]
                            original_end = board[end_pos[0]][end_pos[1]]
                            board[start_pos[0]][start_pos[1]] = '-'
                            board[end_pos[0]][end_pos[1]] = piece

                            # If the move resolves check, it’s not checkmate
                            if not check_check(board, turn):
                                # Revert the move and return False
                                board[start_pos[0]][start_pos[1]] = original_start
                                board[end_pos[0]][end_pos[1]] = original_end
                                return False

                            # Revert the move
                            board[start_pos[0]][start_pos[1]] = original_start
                            board[end_pos[0]][end_pos[1]] = original_end

    return True  # No moves avoid check, so it's checkmate

def is_stalemate(board, turn):
    if check_check(board, turn):
        return False  # If in check, it cannot be stalemate

    # Check if any legal move exists for the player
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if (turn == 'white' and piece.isupper()) or (turn == 'black' and piece.islower()):
                start_pos = (row, col)
                
                # Try moving the piece to all squares on the board
                for end_row in range(ROWS):
                    for end_col in range(COLS):
                        end_pos = (end_row, end_col)
                        
                        # Check if the move is valid and keeps the king out of check
                        if validate_move(board, piece, start_pos, end_pos, turn):
                            # Temporarily make the move
                            original_start = board[start_pos[0]][start_pos[1]]
                            original_end = board[end_pos[0]][end_pos[1]]
                            board[start_pos[0]][start_pos[1]] = '-'
                            board[end_pos[0]][end_pos[1]] = piece

                            # If this move keeps the king out of check, it's not stalemate
                            if not check_check(board, turn):
                                # Revert the move and return False
                                board[start_pos[0]][start_pos[1]] = original_start
                                board[end_pos[0]][end_pos[1]] = original_end
                                return False

                            # Revert the move
                            board[start_pos[0]][start_pos[1]] = original_start
                            board[end_pos[0]][end_pos[1]] = original_end

    return True  # No legal moves available, and not in check, so it’s stalemate

# Function for castling
def validate_castling(board, start, end, turn):
    start_row, start_col = start
    end_row, end_col = end

    if turn == 'white':
        # King-side castling for white
        if start == (7, 4) and end == (7, 6) and not white_king_moved and not white_rook_king_side_moved:
            if board[7][5] == '-' and board[7][6] == '-':
                # Check if passing squares are safe
                if not check_check(board, turn) and not check_check(move_temporary(board, (7, 4), (7, 5)), turn) and not check_check(move_temporary(board, (7, 4), (7, 6)), turn):
                    return "castling_kingside"

        # Queen-side castling for white
        if start == (7, 4) and end == (7, 2) and not white_king_moved and not white_rook_queen_side_moved:
            if board[7][1] == '-' and board[7][2] == '-' and board[7][3] == '-':
                if not check_check(board, turn) and not check_check(move_temporary(board, (7, 4), (7, 3)), turn) and not check_check(move_temporary(board, (7, 4), (7, 2)), turn):
                    return "castling_queenside"

    elif turn == 'black':
        # King-side castling for black
        if start == (0, 4) and end == (0, 6) and not black_king_moved and not black_rook_king_side_moved:
            if board[0][5] == '-' and board[0][6] == '-':
                if not check_check(board, turn) and not check_check(move_temporary(board, (0, 4), (0, 5)), turn) and not check_check(move_temporary(board, (0, 4), (0, 6)), turn):
                    return "castling_kingside"

        # Queen-side castling for black
        if start == (0, 4) and end == (0, 2) and not black_king_moved and not black_rook_queen_side_moved:
            if board[0][1] == '-' and board[0][2] == '-' and board[0][3] == '-':
                if not check_check(board, turn) and not check_check(move_temporary(board, (0, 4), (0, 3)), turn) and not check_check(move_temporary(board, (0, 4), (0, 2)), turn):
                    return "castling_queenside"

    return False  # If none of the castling conditions are met

# Promote pawn if it gets to the last rank
def promote_pawn():
    choice = input("Promote pawn to (Q)ueen, (R)ook, (B)ishop, or (N)ight: ").upper()
    if choice in ['Q', 'R', 'B', 'N']:
        return choice
    return 'Q'  # Default to Queen if input is invalid

# Helper function to temporarily move a piece
def move_temporary(board, start, end):
    temp_board = [row[:] for row in board]
    piece = temp_board[start[0]][start[1]]
    temp_board[start[0]][start[1]] = '-'
    temp_board[end[0]][end[1]] = piece
    return temp_board

# Move pieces
def move_piece(board, start, end):
    global white_king_moved, black_king_moved
    global white_rook_king_side_moved, white_rook_queen_side_moved
    global black_rook_king_side_moved, black_rook_queen_side_moved
    global en_passant_square

    piece = board[start[0]][start[1]]
    board[start[0]][start[1]] = '-'
    board[end[0]][end[1]] = piece

    # Track king and rook movements
    if piece == 'K':
        white_king_moved = True
    elif piece == 'k':
        black_king_moved = True
    elif piece == 'R' and start == (7, 7):  # White king-side rook
        white_rook_king_side_moved = True
    elif piece == 'R' and start == (7, 0):  # White queen-side rook
        white_rook_queen_side_moved = True
    elif piece == 'r' and start == (0, 7):  # Black king-side rook
        black_rook_king_side_moved = True
    elif piece == 'r' and start == (0, 0):  # Black queen-side rook
        black_rook_queen_side_moved = True

    # Check for pawn promotion
    if piece == 'P' and end[0] == 0:  # White pawn reaches the last rank
        board[end[0]][end[1]] = promote_pawn()
    elif piece == 'p' and end[0] == 7:  # Black pawn reaches the last rank
        board[end[0]][end[1]] = promote_pawn().lower()

    # Reset en passant square after each move
    old_en_passant_square = en_passant_square
    en_passant_square = None

    # Check for two-square pawn advance to set en passant target
    if piece == 'P' and start[0] == 6 and end[0] == 4:
        en_passant_square = (5, end[1])  # White pawn's target
    elif piece == 'p' and start[0] == 1 and end[0] == 3:
        en_passant_square = (2, end[1])  # Black pawn's target

    # En passant capture handling
    if piece.lower() == 'p' and old_en_passant_square == end and abs(start[1] - end[1]) == 1:
        capture_row = start[0] # Row of the captured pawn
        board[capture_row][end[1]] = '-'  # Remove the opponent’s pawn

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
                    piece = board[start_row][start_col]
                    if validate_move(board, board[start_row][start_col], selected_square, (row, col), turn):
                        move_piece(board, selected_square, (row, col))
                        turn = 'black' if turn == 'white' else 'white'  # Switch turns
                        # After moving a piece and switching turns
                        if is_checkmate(board, turn):
                            print(f"Checkmate! {turn} loses.")
                            running = False  # End the game 
                        elif is_stalemate(board, turn):
                            print("Stalemate! It's a draw.")
                            running = False  # End the game 

                    # Castling logic
                    castling_result = validate_castling(board, (start_row, start_col), (row, col), turn)
                    if castling_result == 'castling_kingside':
                        # Move king and rook for king-side castling
                        move_piece(board, (start_row, 4), (start_row, 6))  # King
                        move_piece(board, (start_row, 7), (start_row, 5))  # Rook
                        turn = 'black' if turn == 'white' else 'white'  # Switch turns
                    elif castling_result == 'castling_queenside':
                        # Move king and rook for queen-side castling
                        move_piece(board, (start_row, 4), (start_row, 2))  # King
                        move_piece(board, (start_row, 0), (start_row, 3))  # Rook
                        turn = 'black' if turn == 'white' else 'white'  # Switch turns
                    selected_square = None
                else:
                    selected_square = (row, col)

        clock.tick(60)

if __name__ == "__main__":
    main()
