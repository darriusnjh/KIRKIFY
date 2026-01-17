import pygame
import sys
from typing import List, Callable, Optional


class GameMenu:
    """Main menu for 67 Games."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("67 Games")
        self.clock = pygame.time.Clock()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.subtitle_font = pygame.font.Font(None, 24)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (100, 150, 255)
        self.DARK_BLUE = (50, 100, 200)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        
        # Menu state
        self.selected_index = 0
        self.games = []  # List of (name, description, callback)
        self.running = True
        
    def add_game(self, name: str, description: str, callback: Callable):
        """Add a game to the menu."""
        self.games.append((name, description, callback))
    
    def handle_input(self):
        """Handle keyboard input for menu navigation."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.games)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.games)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Launch selected game
                    if self.games:
                        _, _, callback = self.games[self.selected_index]
                        try:
                            callback()
                        except SystemExit:
                            # Game exited, return to menu
                            pass
                        return True  # Continue menu after game
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def draw(self):
        """Draw the menu."""
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = self.title_font.render("67 Games", True, self.YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.subtitle_font.render("Select a game using arrow keys and press ENTER", True, self.GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 130))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Game list
        start_y = 200
        spacing = 80
        
        for i, (name, description, _) in enumerate(self.games):
            y_pos = start_y + i * spacing
            
            # Highlight selected game
            if i == self.selected_index:
                # Draw background highlight
                highlight_rect = pygame.Rect(50, y_pos - 10, self.screen_width - 100, 60)
                pygame.draw.rect(self.screen, self.DARK_BLUE, highlight_rect)
                pygame.draw.rect(self.screen, self.BLUE, highlight_rect, 3)
                
                # Draw selection arrow
                arrow_text = self.menu_font.render(">", True, self.YELLOW)
                self.screen.blit(arrow_text, (60, y_pos))
            
            # Game name
            color = self.YELLOW if i == self.selected_index else self.WHITE
            name_text = self.menu_font.render(name, True, color)
            self.screen.blit(name_text, (100, y_pos))
            
            # Description
            desc_text = self.subtitle_font.render(description, True, self.GRAY)
            self.screen.blit(desc_text, (100, y_pos + 35))
        
        # Instructions
        if self.games:
            instructions = [
                "UP/DOWN: Navigate",
                "ENTER: Select game",
                "ESC: Exit"
            ]
            y_offset = self.screen_height - 100
            for i, instruction in enumerate(instructions):
                inst_text = self.subtitle_font.render(instruction, True, self.GRAY)
                self.screen.blit(inst_text, (50, y_offset + i * 25))
        
        pygame.display.flip()
    
    def run(self):
        """Run the menu loop."""
        while self.running:
            if not self.handle_input():
                break
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
