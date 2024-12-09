# chess_board.py

from pprint import pprint


class ChessBoard:
    def __init__(self):
        """
        Initializes the chessboard with pieces in their starting positions and sets game state variables.
        """
        self.board = self._initialize_board()
        self.move_history = []
        self.king_positions = [(7, 4), (0, 4)] # Track king positions
        self.piece_positions = self._initialize_piece_positions() # Track piece positions
        self.castling_rights = {'white': {'king_side': True, 'queen_side': True},
                                'black': {'king_side': True, 'queen_side': True}}
        self.en_passant_target = None  # Square eligible for en passant capture
        self.turn = 'white'

    def _initialize_piece_positions(self):
        """
        Creates the initial hash map of piece positions.
        Returns:
            dict: A dictionary mapping each piece type to its list of positions.
        """
        positions = {}
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '..':
                    if piece not in positions:
                        positions[piece] = []
                    positions[piece].append((row, col))
        return positions

    def _initialize_board(self):
        """
        Creates the starting position of the chessboard.
        Returns:
            list: 8x8 grid with piece representation (e.g., 'wP' for white pawn, 'bK' for black king).
        """
        board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],  # Black pieces
            ['bP'] * 8,                                        # Black pawns
            ['..'] * 8,                                        # Empty squares
            ['..'] * 8,
            ['..'] * 8,
            ['..'] * 8,
            ['wP'] * 8,                                        # White pawns
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],  # White pieces
        ]
        return board

    def display_board(self):
        """
        Prints the chessboard in a human-readable format.
        """
        for row in self.board:
            print(' '.join(row))
        print()

    def is_path_clear(self, start, end):
        """
        Checks if the path between two squares is clear (no obstructing pieces).
        Args:
            start (tuple): Starting position (row, col).
            end (tuple): Ending position (row, col).
        Returns:
            bool: True if the path is clear, False otherwise.
        """
        # Horizontal or vertical movement
        row_start, col_start = start
        row_end, col_end = end

        if row_start == row_end:  # Horizontal
            step = 1 if col_end > col_start else -1
            for col in range(col_start + step, col_end, step):
                if self.board[row_start][col] != '..':
                    return False
        elif col_start == col_end:  # Vertical
            step = 1 if row_end > row_start else -1
            for row in range(row_start + step, row_end, step):
                if self.board[row][col_start] != '..':
                    return False
        else:  # Diagonal
            row_step = 1 if row_end > row_start else -1
            col_step = 1 if col_end > col_start else -1
            row, col = row_start + row_step, col_start + col_step
            while row != row_end and col != col_end:
                if self.board[row][col] != '..':
                    return False
                row += row_step
                col += col_step

        return True

    def generate_legal_moves(self, color):
        """
        Generates all legal moves for the current player.
        Args:
            color (str): The color of the player ('white' or 'black').
        Returns:
            list: List of legal moves [(start_pos, end_pos)].
        """
        legal_moves = []
        player_prefix = 'w' if color == 'white' else 'b'

        # Iterate through the player's pieces using piece_positions
        for piece, positions in self.piece_positions.items():
            if piece.startswith(player_prefix):
                for position in positions:
                    legal_moves.extend(self._get_piece_moves(position, piece))

        return legal_moves

    def _get_piece_moves(self, position, piece):
        """
        Helper function to get all legal moves for a specific piece.
        Args:
            position (tuple): Position of the piece (row, col).
            piece (str): The piece at the position (e.g., 'wP', 'bK').
        Returns:
            list: List of legal moves [(start_pos, end_pos)].
        """
        moves = []
        color = 'white' if piece[0] == 'w' else 'black'
        row, col = position
    
        if piece[1] == 'P':  # Pawn
            moves.extend(self._get_pawn_moves(position, piece))
        elif piece[1] == 'B':  # Bishop
            moves.extend(self._get_bishop_moves(position, piece))
        elif piece[1] == 'N':  # Knight
            moves.extend(self._get_knight_moves(position, piece))
        elif piece[1] == 'K':  # King
            moves.extend(self._get_king_moves(position, piece))
        elif piece[1] == 'R':  # Rook
            moves.extend(self._get_rook_moves(position, piece))
        elif piece[1] == 'Q':  # Queen
            moves.extend(self._get_queen_moves(position, piece))
    
        # Filter out moves that would put the king in check
        return [move for move in moves if not self.move_puts_king_in_check(move, color)]

    def _get_opponent_piece_moves(self, position, piece):
        """
        Generates possible moves for an opponent piece without recursion.
        Args:
            position (tuple): Position of the piece (row, col).
            piece (str): The opponent piece at the position.
        Returns:
            list: List of potential moves [(start_pos, end_pos)].
        """
        moves = []
        if piece[1] == 'P':  # Pawn
            moves.extend(self._get_pawn_moves(position, piece))
        elif piece[1] == 'B':  # Bishop
            moves.extend(self._get_bishop_moves(position, piece))
        elif piece[1] == 'N':  # Knight
            moves.extend(self._get_knight_moves(position, piece))
        elif piece[1] == 'K':  # King
            moves.extend(self._get_king_moves(position, piece, False))
        elif piece[1] == 'R':  # Rook
            moves.extend(self._get_rook_moves(position, piece))
        elif piece[1] == 'Q':  # Queen
            moves.extend(self._get_queen_moves(position, piece))
        return moves


    def _get_pawn_moves(self, position, piece):
        """
        Generates legal moves for a pawn.
        Args:
            position (tuple): Position of the pawn (row, col).
            piece (str): The pawn ('wP' or 'bP').
        Returns:
            list: List of potential pawn moves [(start_pos, end_pos)].
        """
        moves = []
        direction = -1 if piece.startswith('w') else 1
        row, col = position

        # Single step forward
        if self.board[row + direction][col] == '..':
            moves.append(((row, col), (row + direction, col)))

        # Double step forward (only from starting position)
        if (row == 6 and piece.startswith('w')) or (row == 1 and piece.startswith('b')):
            if self.board[row + direction][col] == '..' and self.board[row + 2 * direction][col] == '..':
                moves.append(((row, col), (row + 2 * direction, col)))

        # Captures
        for offset in [-1, 1]:  # Left and right diagonal
            capture_col = col + offset
            if 0 <= capture_col < 8 and self.board[row + direction][capture_col].startswith('b' if piece.startswith('w') else 'w'):
                moves.append(((row, col), (row + direction, capture_col)))

        # En passant
        if self.en_passant_target:
            target_row, target_col = self.en_passant_target
            if abs(target_col - col) == 1 and target_row == row + direction:
                # Ensure the en passant target is an opponent's pawn
                en_passant_piece = self.board[row][target_col]  # Piece on the en passant target column
                if en_passant_piece.startswith('b' if piece.startswith('w') else 'w'):  # Must be an opponent's pawn
                    moves.append(((row, col), (target_row, target_col)))

        return moves
        
    def _get_bishop_moves(self, position, piece):
        """
        Generates legal moves for a bishop.
        Args:
            position (tuple): Position of the bishop (row, col).
            piece (str): The bishop ('wB' or 'bB').
        Returns:
            list: List of potential bishop moves [(start_pos, end_pos)].
        """
        moves = []
        row, col = position
    
        # Directions for diagonal movement (row_delta, col_delta)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    
        for row_delta, col_delta in directions:
            current_row, current_col = row + row_delta, col + col_delta
    
            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target_square = self.board[current_row][current_col]
    
                if target_square == '..':  # Empty square
                    moves.append(((row, col), (current_row, current_col)))
                elif target_square.startswith(piece[0]):  # Own piece, block further movement
                    break
                else:  # Opponent's piece, capture allowed, but stop further movement
                    moves.append(((row, col), (current_row, current_col)))
                    break
    
                # Move to the next square in the current direction
                current_row += row_delta
                current_col += col_delta
    
        return moves
        
    def _get_knight_moves(self, position, piece):
        """
        Generates legal moves for a knight.
        Args:
            position (tuple): Position of the knight (row, col).
            piece (str): The knight ('wN' or 'bN').
        Returns:
            list: List of potential knight moves [(start_pos, end_pos)].
        """
        moves = []
        row, col = position
        
        # Directions for l-shaped movement (row_delta, col_delta)
        directions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
        
        for row_delta, col_delta in directions:
            current_row, current_col = row + row_delta, col + col_delta
            
            if 0 <= current_row < 8 and 0 <= current_col < 8:
                target_square = self.board[current_row][current_col]
                if target_square == '..': # Empty Square
                    moves.append(((row, col), (current_row, current_col)))
                elif not target_square.startswith(piece[0]): # Make sure we dont capture our own piece
                    moves.append(((row, col), (current_row, current_col)))
        
        return moves
        
    def _get_rook_moves(self, position, piece):
        """
        Generates legal moves for a rook.
        Args:
            position (tuple): Position of the rook (row, col).
            piece (str): The rook ('wR' or 'bR').
        Returns:
            list: List of potential rook moves [(start_pos, end_pos)].
        """
        moves = []
        row, col = position
    
        # Directions for horizontal and vertical movement (row_delta, col_delta)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
        for row_delta, col_delta in directions:
            current_row, current_col = row + row_delta, col + col_delta
    
            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target_square = self.board[current_row][current_col]
    
                if target_square == '..':  # Empty square
                    moves.append(((row, col), (current_row, current_col)))
                elif target_square.startswith(piece[0]):  # Own piece, block further movement
                    break
                else:  # Opponent's piece, capture allowed, but stop further movement
                    moves.append(((row, col), (current_row, current_col)))
                    break
    
                # Move to the next square in the current direction
                current_row += row_delta
                current_col += col_delta
    
        return moves
    
    def _get_king_moves(self, position, piece, validate_castling=True):
        """
        Generates legal moves for a king.
        Args:
            position (tuple): Position of the king (row, col).
            piece (str): The king ('wK' or 'bK').
            validate_castling (bool): Whether to add castling moves or not
        Returns:
            list: List of potential knight moves [(start_pos, end_pos)].
        """
        moves = []
        row, col = position
        color = 'white' if piece[0] == 'w' else 'black'
        
        # Directions for  movement (row_delta, col_delta)
        directions = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
        
        for row_delta, col_delta in directions:
            current_row, current_col = row + row_delta, col + col_delta
            
            if 0 <= current_row < 8 and 0 <= current_col < 8:
                target_square = self.board[current_row][current_col]
                if target_square == '..': # Empty Square
                    moves.append(((row, col), (current_row, current_col)))
                elif not target_square.startswith(piece[0]): # Make sure we dont capture our own piece
                    moves.append(((row, col), (current_row, current_col)))

            # Castling moves
        if validate_castling:
            if self.can_castle(color, 'king_side'):
                moves.append(((row, col), (row, col + 2)))
            if self.can_castle(color, 'queen_side'):
                moves.append(((row, col), (row, col - 2)))
            
        return moves
        
    def _get_queen_moves(self, position, piece):
        """
        Generates legal moves for a queen.
        Args:
            position (tuple): Position of the queen (row, col).
            piece (str): The queen ('wQ' or 'bQ').
        Returns:
            list: List of potential rook moves [(start_pos, end_pos)].
        """
        moves = []
        row, col = position
    
        # Directions for horizontal, vertical and diagonal movement (row_delta, col_delta)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    
        for row_delta, col_delta in directions:
            current_row, current_col = row + row_delta, col + col_delta
    
            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target_square = self.board[current_row][current_col]
    
                if target_square == '..':  # Empty square
                    moves.append(((row, col), (current_row, current_col)))
                elif target_square.startswith(piece[0]):  # Own piece, block further movement
                    break
                else:  # Opponent's piece, capture allowed, but stop further movement
                    moves.append(((row, col), (current_row, current_col)))
                    break
    
                # Move to the next square in the current direction
                current_row += row_delta
                current_col += col_delta
    
        return moves
    
    def execute_move(self, move):
        """
        Executes a given move on the board, updates game state variables, 
        and handles special cases like promotion, castling, and en passant.
        Args:
            move (tuple): The move to execute, in the format ((start_row, start_col), (end_row, end_col)).
        """
        start_pos, end_pos = move
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        moving_piece = self.board[start_row][start_col]
        captured_piece = self.board[end_row][end_col]

        # Move the piece to the new position
        self.board[end_row][end_col] = moving_piece
        self.board[start_row][start_col] = '..'

        print(moving_piece, start_pos, end_pos)
        # Update piece_positions
        self.piece_positions[moving_piece].remove(start_pos)
        self.piece_positions[moving_piece].append(end_pos)

        # If a piece was captured, remove its position
        if captured_piece != '..':
            self.piece_positions[captured_piece].remove(end_pos)
            if not self.piece_positions[captured_piece]:  # If no instances of the piece remain
                del self.piece_positions[captured_piece]
    
        # Update move history
        self.move_history.append(move)
    
        # Update king position if the king moved
        if moving_piece[1] == 'K':
            if moving_piece.startswith('w'):
                self.king_positions[0] = end_pos  # Update white king's position
            else:
                self.king_positions[1] = end_pos  # Update black king's position

        # Handle special cases
        if moving_piece[1] == 'P':  # Pawn
            self._handle_pawn_special_cases(start_pos, end_pos)
        elif moving_piece[1] == 'K':  # King
            self._handle_castling(start_pos, end_pos)
    
        # Update game state variables
        self._update_castling_rights(moving_piece, start_pos)
        self._update_en_passant(moving_piece, start_pos, end_pos)
    
        # Switch turn
        self.turn = 'black' if self.turn == 'white' else 'white'

        pprint(self.piece_positions)
    
    def temp_move(self, move):
        """
        Temporarily makes a move on the board and returns the previous state for restoration.
        Args:
            move (tuple): The move to execute, in the format ((start_row, start_col), (end_row, end_col)).
        Returns:
            tuple: A tuple containing the previous state of the end position and the moving piece.
        """
        start_pos, end_pos = move
        start_row, start_col = start_pos
        end_row, end_col = end_pos
    
        # Save the previous state of the board
        previous_end_piece = self.board[end_row][end_col]
        moving_piece = self.board[start_row][start_col]
    
        # Temporarily make the move
        self.board[end_row][end_col] = moving_piece
        self.board[start_row][start_col] = '..'
    
        return previous_end_piece, moving_piece
    
    def is_check(self, color):
        """
        Checks if the current player's king is in check without generating all opponent moves.
        Args:
            color (str): The color of the player ('white' or 'black').
        Returns:
            bool: True if the king is in check, False otherwise.
        """
        # Get the king's position
        king_position = self.king_positions[0] if color == 'white' else self.king_positions[1]

        # Check if any opponent piece attacks the king's position
        opponent_color = 'b' if color == 'white' else 'w'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece.startswith(opponent_color):  # Opponent's piece
                    moves = self._get_opponent_piece_moves((row, col), piece)
                    if any(move[1] == king_position for move in moves):  # King is under attack
                        return True

        return False
    
    def is_check_on_position(self, position, color):
        """
        Checks if a specific position is under attack by opponent pieces.
        Args:
            position (tuple): The position to check (row, col).
            color (str): The color of the player ('white' or 'black').
        Returns:
            bool: True if the position is under attack, False otherwise.
        """
        opponent_prefix = 'b' if color == 'white' else 'w'

        # Iterate through opponent pieces only
        for piece, positions in self.piece_positions.items():
            if piece.startswith(opponent_prefix):
                for piece_pos in positions:
                    moves = self._get_opponent_piece_moves(piece_pos, piece)
                    if any(move[1] == position for move in moves):  # Position is attacked
                        return True

        return False

    def move_puts_king_in_check(self, move, color):
        """
        Checks if a move would leave the player's king in check.
        Args:
            move (tuple): The move to test, in the format ((start_row, start_col), (end_row, end_col)).
            color (str): The color of the player ('white' or 'black').
        Returns:
            bool: True if the move leaves the king in check, False otherwise.
        """
        start_pos, end_pos = move
        previous_end_piece, moving_piece = self.temp_move(move)

        # Temporarily update the king's position if it's moving
        original_king_position = None
        if moving_piece[1] == 'K':
            if color == 'white':
                original_king_position = self.king_positions[0]
                self.king_positions[0] = end_pos
            else:
                original_king_position = self.king_positions[1]
                self.king_positions[1] = end_pos

        # Check if the king is in check
        in_check = self.is_check(color)

        # Restore the previous board state
        self.board[end_pos[0]][end_pos[1]] = previous_end_piece
        self.board[start_pos[0]][start_pos[1]] = moving_piece

        # Restore the original king position if updated
        if moving_piece[1] == 'K' and original_king_position:
            if color == 'white':
                self.king_positions[0] = original_king_position
            else:
                self.king_positions[1] = original_king_position

        return in_check

    def is_checkmate(self, color):
        """
        Returns True if player is checkmated
        """
        return self.is_check(color) and len(self.generate_legal_moves(color)) == 0
    
    def is_stalemate(self, color):
        """
        Returns True if player is stalemated
        """
        return not self.is_check(color) and len(self.generate_legal_moves(color)) == 0

    def _handle_pawn_special_cases(self, start_pos, end_pos):
        """
        Handles special cases for pawns, such as promotion and en passant.
        """
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        moving_piece = self.board[end_row][end_col]
        other_piece = 'wP' if moving_piece == 'bP' else 'bP'
    
        # Promotion
        if (moving_piece == 'wP' and end_row == 0) or (moving_piece == 'bP' and end_row == 7):
            promoting_to = self._promote_pawn()
            self.board[end_row][end_col] = promoting_to
            self.piece_positions[moving_piece].remove((end_row, end_col)) # Remove the pawn from the list of pawns in piece position
            if promoting_to in self.piece_positions.keys(): # Make sure the promoting piece is still in piece positions
                self.piece_positions[promoting_to].append((end_row, end_col)) # Add the position of the promoting piece to piece positions
            else:
                self.piece_positions[promoting_to] = []
                self.piece_positions[promoting_to].append((end_row, end_col))
    
        # En passant capture
        if self.en_passant_target == end_pos:
            print('En passant capture')
            self.board[start_row][end_col] = '..'
            self.piece_positions[other_piece].remove((start_row, end_col)) # Update piece positions to make sure captured pawn is removed

    def can_castle(self, color, side):
        """
        Determines if castling is legal for the given color and side (king-side or queen-side).
        Args:
            color (str): 'white' or 'black', representing the player.
            side (str): 'king_side' or 'queen_side', representing the side to castle.
        Returns:
            bool: True if castling is legal, False otherwise.
        """
        # Define rows and columns for king and rook positions
        row = 7 if color == 'white' else 0
        king_col = 4
        rook_col = 7 if side == 'king_side' else 0
        col_step = 1 if side == 'king_side' else -1

        # Check if castling rights exist
        if not self.castling_rights[color][side]:
            return False

        # Check if path between king and rook is clear
        for col in range(king_col + col_step, rook_col, col_step):
            if self.board[row][col] != '..':
                return False

        # Ensure the king does not pass through or land in check
        for col in range(king_col, king_col + 3 * col_step, col_step):  # 3 positions to check (current, next, and end)
            temp_position = (row, col)
            if self.is_check_on_position(temp_position, color):
                return False

        return True

    def _handle_castling(self, start_pos, end_pos):
        """
        Handles castling if the move is a king's castling move.
        """
        if abs(start_pos[1] - end_pos[1]) == 2:  # Castling detected
            if end_pos[1] > start_pos[1]:  # King-side castling
                rook_start = (start_pos[0], 7)
                rook_end = (start_pos[0], 5)
            else:  # Queen-side castling
                rook_start = (start_pos[0], 0)
                rook_end = (start_pos[0], 3)
            piece = self.board[rook_start[0]][rook_start[1]][0] + "R"
        
            # Move the rook
            self.board[rook_end[0]][rook_end[1]] = self.board[rook_start[0]][rook_start[1]]
            self.board[rook_start[0]][rook_start[1]] = '..'

            # Update the rook position
            self.piece_positions[piece].remove(rook_start)
            self.piece_positions[piece].append(rook_end)
    
    def _update_castling_rights(self, moving_piece, start_pos):
        """
        Updates castling rights if a king or rook has moved.
        """
        if moving_piece[1] == 'K':  # King moved
            self.castling_rights[self.turn]['king_side'] = False
            self.castling_rights[self.turn]['queen_side'] = False
        elif moving_piece[1] == 'R':  # Rook moved
            if start_pos == (0, 0) or start_pos == (7, 0):  # Queen-side rook
                self.castling_rights[self.turn]['queen_side'] = False
            elif start_pos == (0, 7) or start_pos == (7, 7):  # King-side rook
                self.castling_rights[self.turn]['king_side'] = False
    
    def _update_en_passant(self, moving_piece, start_pos, end_pos):
        """
        Updates the en passant target square after a pawn's double-step move.
        """
        if moving_piece[1] == 'P':  # Pawn
            if abs(end_pos[0] - start_pos[0]) == 2:  # Double-step move
                self.en_passant_target = ((start_pos[0] + end_pos[0]) // 2, start_pos[1])
            else:
                self.en_passant_target = None
        else:
            self.en_passant_target = None
    
    def _promote_pawn(self):
        """
        Prompts the player to select a piece for pawn promotion.
        Returns:
            str: The chosen piece (e.g., 'wQ' for a white queen).
        """
        # For simplicity in the code, default to a queen
        return f'{self.turn[0]}Q'  # Example: 'wQ' for white
    
# # Testing
# import pprint

# board = ChessBoard()
# board.display_board()
# legal_moves = board.generate_legal_moves('white')
# print('There are', len(legal_moves), 'legal moves for white') # Should give 20
# board.execute_move(((6, 0), (4, 0)))
# board.display_board()
# legal_moves = board.generate_legal_moves('black')
# print('There are', len(legal_moves), 'legal moves for black') # Should give 21
# board.execute_move(((1, 0), (3, 0)))
# board.display_board()
# legal_moves = board.generate_legal_moves('white')
# print('There are', len(legal_moves), 'legal moves for white')
# pprint.pprint(legal_moves)
