import pygame
from game import GameController
from chess_ai import ChessAI

class MainMenu:
    def __init__(self, screen):
        """
        Initializes the main menu.
        Args:
            screen (pygame.Surface): The main display surface.
        """
        self.screen = screen
        self.font = pygame.font.SysFont(None, 50)
        self.running = True
        self.selected_option = None
        self.options = [
            {"label": "Play Against Player", "action": "player"},
            {"label": "Play Against AI", "action": "ai"}
        ]

    def draw_menu(self):
        """
        Draws the main menu options.
        """
        self.screen.fill((30, 30, 30))  # Dark background
        title = self.font.render("Chess Game", True, (255, 255, 255))
        self.screen.blit(title, ((self.screen.get_width() - title.get_width()) // 2, 50))

        for i, option in enumerate(self.options):
            label = self.font.render(option["label"], True, (255, 255, 255))
            x = (self.screen.get_width() - label.get_width()) // 2
            y = 150 + i * 100
            self.screen.blit(label, (x, y))
            option["rect"] = pygame.Rect(x, y, label.get_width(), label.get_height())

        pygame.display.flip()

    def handle_click(self, pos):
        """
        Handles mouse clicks on menu options.
        Args:
            pos (tuple): The (x, y) position of the mouse click.
        """
        for option in self.options:
            if option["rect"].collidepoint(pos):
                self.selected_option = option["action"]
                self.running = False

    def run(self):
        """
        Runs the main menu loop.
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.draw_menu()


class AIDifficultyMenu:
    def __init__(self, screen):
        """
        Initializes the AI difficulty menu.
        Args:
            screen (pygame.Surface): The main display surface.
        """
        self.screen = screen
        self.font = pygame.font.SysFont(None, 50)
        self.running = True
        self.options = [
            {"label": "Easy", "difficulty": "easy"},
            {"label": "Medium", "difficulty": "medium"},
            {"label": "Hard", "difficulty": "hard"}
        ]
        self.selected_difficulty = None

    def draw_menu(self):
        """
        Draws the AI difficulty menu options.
        """
        self.screen.fill((30, 30, 30))  # Dark background
        title = self.font.render("Select AI Difficulty", True, (255, 255, 255))
        self.screen.blit(title, ((self.screen.get_width() - title.get_width()) // 2, 50))

        for i, option in enumerate(self.options):
            label = self.font.render(option["label"], True, (255, 255, 255))
            x = (self.screen.get_width() - label.get_width()) // 2
            y = 150 + i * 100
            self.screen.blit(label, (x, y))
            option["rect"] = pygame.Rect(x, y, label.get_width(), label.get_height())

        pygame.display.flip()

    def handle_click(self, pos):
        """
        Handles mouse clicks on difficulty options.
        Args:
            pos (tuple): The (x, y) position of the mouse click.
        """
        for option in self.options:
            if option["rect"].collidepoint(pos):
                self.selected_difficulty = option["difficulty"]
                self.running = False

    def run(self):
        """
        Runs the AI difficulty menu loop.
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.draw_menu()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((480, 480))  # Main display surface
    pygame.display.set_caption("Chess Game")

    # Show main menu
    main_menu = MainMenu(screen)
    main_menu.run()

    if main_menu.selected_option == "player":
        # Start a two-player game
        GameController(screen).game_loop()
    elif main_menu.selected_option == "ai":
        # Show AI difficulty menu
        ai_menu = AIDifficultyMenu(screen)
        ai_menu.run()
        if ai_menu.selected_difficulty:
            ai = ChessAI(ai_menu.selected_difficulty)
            GameController(screen, ai).game_loop()
