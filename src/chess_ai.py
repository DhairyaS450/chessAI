import random

class ChessAI:
    def __init__(self, difficulty='easy'):
        """
        Initializes the ChessAI with a specified difficulty level.
        Args:
            difficulty (str): 'easy', 'medium', or 'hard'.
        """
        self.difficulty = difficulty

    def choose_move(self, board):
        """
        Chooses a move for the AI based on the difficulty level.
        Args:
            board (ChessBoard): The current game board.
        Returns:
            tuple: The chosen move ((start_row, start_col), (end_row, end_col)).
        """
        if self.difficulty == 'easy':
            return self._random_move(board)
        elif self.difficulty == 'medium':
            return self._basic_evaluation(board)
        elif self.difficulty == 'hard':
            return self._minimax(board, depth=3)
        else:
            raise ValueError("Invalid difficulty level.")

    import random

    def _random_move(self, board):
        """
        Chooses a random legal move for the AI.
        Args:
            board (ChessBoard): The current game board.
        Returns:
            tuple: A randomly chosen legal move.
        """
        board.display_board()

        legal_moves = board.generate_legal_moves(board.turn)
        return random.choice(legal_moves) if legal_moves else None

    def _basic_evaluation(self, board):
        """
        Chooses a move based on a basic evaluation function.
        Args:
            board (ChessBoard): The current game board.
        Returns:
            tuple: The move with the highest evaluation score.
        """
        def evaluate_move(move):
            start, end = move
            target_piece = board.board[end[0]][end[1]]
            # Assign values to pieces (higher for more valuable pieces)
            piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
            return piece_values.get(target_piece[1], 0) if target_piece != '..' else 0

        legal_moves = board.generate_legal_moves(board.turn)
        if not legal_moves:
            return None

        # Choose the move with the highest evaluation
        return max(legal_moves, key=evaluate_move)

    def _minimax(self, board, depth, maximizing_player=True, alpha=float('-inf'), beta=float('inf')):
        """
        Implements the minimax algorithm with alpha-beta pruning.
        Args:
            board (ChessBoard): The current game board.
            depth (int): The search depth.
            maximizing_player (bool): True if the AI is maximizing, False if minimizing.
            alpha (float): Alpha value for pruning.
            beta (float): Beta value for pruning.
        Returns:
            tuple: (evaluation, move) - The best evaluation and the corresponding move.
        """
        if depth == 0 or board.is_checkmate('white') or board.is_stalemate('white'):
            return self._evaluate_board(board), None

        legal_moves = board.generate_legal_moves(board.turn)
        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in legal_moves:
                board.execute_move(move)
                eval, _ = self._minimax(board, depth - 1, False, alpha, beta)
                board.undo_move()  # Restore board state
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in legal_moves:
                board.execute_move(move)
                eval, _ = self._minimax(board, depth - 1, True, alpha, beta)
                board.undo_move()  # Restore board state
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def _evaluate_board(self, board):
        """
        Evaluates the board position for the AI.
        Args:
            board (ChessBoard): The current game board.
        Returns:
            int: The evaluation score (positive for advantage, negative for disadvantage).
        """
        piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        score = 0
        for piece, positions in board.piece_positions.items():
            value = piece_values.get(piece[1], 0)
            score += value * len(positions) if piece.startswith('w') else -value * len(positions)
        return score
