import pygame
from pprint import pprint
from chess_board import ChessBoard

class GameController:
    def __init__(self, screen, ai=None):
        """
        Initializes the game controller, including the chessboard and pygame.
        """
        pygame.init()
        self.screen = screen  # 480x480 pixel window
        self.ai = ai
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()

        # Chessboard and game state
        self.board = ChessBoard()
        self.selected_piece = None  # Currently selected piece (row, col)
        self.legal_moves = []       # Legal moves for the selected piece
        self.running = True         # Main game loop flag

        # Load piece images
        self.piece_images = self._load_piece_images()

    def _load_piece_images(self):
        """
        Loads images for chess pieces and returns a dictionary mapping pieces to images.
        """
        images = {}
        piece_types = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
        for piece in piece_types:
            images[piece] = pygame.image.load(f'assets/pieces/{piece}.png')
        return images

    def draw_board(self):
        """
        Draws the chessboard and all pieces.
        """
        colors = [pygame.Color(240, 217, 181), pygame.Color(181, 136, 99)]  # Light and dark squares
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(col * 60, row * 60, 60, 60))

                # Draw piece if present
                piece = self.board.board[row][col]
                if piece != '..':
                    self.screen.blit(self.piece_images[piece], (col * 60, row * 60))

    def highlight_moves(self):
        """
        Highlights the selected piece and its legal moves.
        """
        if self.selected_piece:
            row, col = self.selected_piece
            pygame.draw.rect(self.screen, pygame.Color(0, 255, 0, 100),
                             pygame.Rect(col * 60, row * 60, 60, 60), 5)  # Highlight selected piece

            for move in self.legal_moves:
                _, end_pos = move
                r, c = end_pos
                pygame.draw.circle(self.screen, pygame.Color(0, 255, 0),
                                   (c * 60 + 30, r * 60 + 30), 10)  # Highlight possible moves

    def handle_click(self, pos):
        """
        Handles mouse clicks to select pieces and make moves.
        Args:
            pos (tuple): (x, y) position of the mouse click in pixels.
        """
        col, row = pos[0] // 60, pos[1] // 60  # Convert pixel coordinates to board indices

        if self.selected_piece:  # A piece is already selected
            move = (self.selected_piece, (row, col))
            if move in self.legal_moves:  # Valid move
                self.board.execute_move(move)
                self.selected_piece = None
                self.legal_moves = []
                self.check_game_over()

                # If AI is playing the next turn, ensure it uses the updated board state
                if self.ai and self.board.turn == 'black': # Assuming AI plays black
                    self.ai_turn()
            else:  # Invalid move, deselect
                self.selected_piece = None
                self.legal_moves = []
        else:  # No piece is selected
            if 0 <= row < 8 and 0 <= col < 8:
                piece = self.board.board[row][col]
                if piece.startswith(self.board.turn[0]):  # Select a piece of the current player
                    self.selected_piece = (row, col)
                    self.legal_moves = self.board._get_piece_moves((row, col), piece)

    def ai_turn(self):
        """
        Executes the AI's turn after the board is updated.
        """
        legal_moves = self.board.generate_legal_moves(self.board.turn)  # Use updated board state
        ai_move = self.ai.choose_move(self.board)  # Choose a move
        if ai_move in legal_moves:  # Ensure move is valid
            self.board.execute_move(ai_move)
            self.check_game_over()  # Check for game-ending conditions
        else:
            raise ValueError("AI attempted an illegal move!")

    def handle_ai_turn(self):
        """
        Handles the AI's turn by generating and executing its move.
        """
        if self.board.turn == 'black':  # Assuming AI plays as black
            ai_move = self.ai.choose_move(self.board)
            if ai_move:
                self.board.execute_move(ai_move)
                self.check_game_over()  # Check for game-ending conditions

    def check_game_over(self):
        """
        Checks for game-ending conditions (checkmate or stalemate) and handles them.
        """
        # Generate legal moves for the current player
        legal_moves = self.board.generate_legal_moves(self.board.turn)

        if not legal_moves:  # No legal moves
            if self.board.is_check(self.board.turn):
                self.show_popup("Checkmate", f"{self.board.turn.capitalize()} is checkmated! "
                                            f"{'Black' if self.board.turn == 'white' else 'White'} wins.")
            else:
                self.show_popup("Stalemate", "The game is a draw by stalemate.")

    def show_popup(self, title, message):
        """
        Displays a popup message using pygame for game-ending conditions.
        Args:
            title (str): The title of the popup.
            message (str): The message to display.
        """
        popup_width, popup_height = 400, 200
        popup_x = (self.screen.get_width() - popup_width) // 2
        popup_y = (self.screen.get_height() - popup_height) // 2

        # Create the popup surface
        popup = pygame.Surface((popup_width, popup_height))
        popup.fill((200, 200, 200))  # Light gray background
        pygame.draw.rect(popup, (0, 0, 0), popup.get_rect(), 5)  # Black border

        # Display the title
        font_title = pygame.font.SysFont(None, 36)
        title_text = font_title.render(title, True, (0, 0, 0))
        popup.blit(title_text, ((popup_width - title_text.get_width()) // 2, 20))

        # Display the message
        font_message = pygame.font.SysFont(None, 28)
        message_text = font_message.render(message, True, (0, 0, 0))
        popup.blit(message_text, ((popup_width - message_text.get_width()) // 2, 80))

        # Define button dimensions and positions
        restart_button_rect = pygame.Rect((popup_width // 4 - 50, 130, 100, 40))
        quit_button_rect = pygame.Rect((3 * popup_width // 4 - 50, 130, 100, 40))

        # Draw buttons on the popup
        pygame.draw.rect(popup, (0, 128, 0), restart_button_rect)  # Green for restart
        pygame.draw.rect(popup, (128, 0, 0), quit_button_rect)     # Red for quit

        # Display button text
        font_buttons = pygame.font.SysFont(None, 32)
        restart_text = font_buttons.render("Restart", True, (255, 255, 255))
        quit_text = font_buttons.render("Quit", True, (255, 255, 255))

        popup.blit(restart_text, (restart_button_rect.x + (restart_button_rect.width - restart_text.get_width()) // 2,
                                restart_button_rect.y + (restart_button_rect.height - restart_text.get_height()) // 2))
        popup.blit(quit_text, (quit_button_rect.x + (quit_button_rect.width - quit_text.get_width()) // 2,
                            quit_button_rect.y + (quit_button_rect.height - quit_text.get_height()) // 2))

        # Display the popup and handle interactions
        running_popup = True
        while running_popup:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # Adjust mouse positions relative to popup location
                    adjusted_x = mouse_x - popup_x
                    adjusted_y = mouse_y - popup_y

                    if restart_button_rect.collidepoint(adjusted_x, adjusted_y):
                        self.restart_game()
                        running_popup = False
                    elif quit_button_rect.collidepoint(adjusted_x, adjusted_y):
                        pygame.quit()
                        exit()

            # Render popup
            self.screen.blit(popup, (popup_x, popup_y))
            pygame.display.flip()


    def restart_game(self):
        """
        Resets the game state to the initial setup for a new game.
        """
        self.board = ChessBoard()  # Reinitialize the chessboard
        self.selected_piece = None
        self.legal_moves = []
        self.running = True  # Resume the game loop

    def game_loop(self):
        """
        Main game loop for handling events and rendering the game.
        """
        while self.running:
            if self.ai and self.board.turn == 'black':  # AI's turn (assuming AI plays as black)
                legal_moves = self.board.generate_legal_moves(self.board.turn)
                ai_move = self.ai.choose_move(self.board)
                if ai_move in legal_moves:  # Validate AI move
                    self.board.execute_move(ai_move)
                    self.check_game_over()  # Check for game-ending conditions
                else:
                    raise ValueError("AI attempted an illegal move!")
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            # Draw the board and update the screen
            self.draw_board()
            self.highlight_moves()
            pygame.display.flip()
            pygame.time.Clock().tick(60)

        pygame.quit()

# game = GameController()
# game.__init__()
# game.game_loop()
