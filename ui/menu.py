import pygame
import sys
from typing import List, Callable, Optional
from core.ui_utils import UITheme
from ui import settings


class GameMenu:
    """Main menu for 67 Games."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600, settings: bool = False):
        pygame.init()
        self.settings = settings

        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width, self.screen_height = self.screen.get_size()
        else:
            w, h = self.settings.window_size
            self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
            self.screen_width, self.screen_height = w, h
        pygame.display.set_caption("67 Games")
        self.clock = pygame.time.Clock()
        
        # Use responsive fonts from UITheme
        title_size = UITheme.get_responsive_font_size(72, screen_height, 48)
        menu_size = UITheme.get_responsive_font_size(48, screen_height, 32)
        subtitle_size = UITheme.get_responsive_font_size(24, screen_height, 18)
        
        self.title_font = pygame.font.Font(None, title_size)
        self.menu_font = pygame.font.Font(None, menu_size)
        self.subtitle_font = pygame.font.Font(None, subtitle_size)
        
        # Use UITheme colors
        self.BLACK = UITheme.BG_DARK
        self.WHITE = UITheme.TEXT_PRIMARY
        self.BLUE = UITheme.ACCENT_PRIMARY
        self.DARK_BLUE = UITheme.BG_LIGHT
        self.YELLOW = UITheme.ACCENT_SECONDARY
        self.GRAY = UITheme.TEXT_SECONDARY
        
        # Menu state
        self.selected_index = 0
        self.games = []  # List of (name, description, callback)
        self.running = True
        
    def add_game(self, name: str, description: str, callback: Callable):
        """Add a game to the menu."""
        self.games.append((name, description, callback))
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.settings.fullscreen = not self.settings.fullscreen

        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width, self.screen_height = self.screen.get_size()
        else:
            w, h = self.settings.window_size
            self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
            self.screen_width, self.screen_height = w, h
        
        # Update fonts for new screen size
        title_size = UITheme.get_responsive_font_size(72, self.screen_height, 48)
        menu_size = UITheme.get_responsive_font_size(48, self.screen_height, 32)
        subtitle_size = UITheme.get_responsive_font_size(24, self.screen_height, 18)
        self.title_font = pygame.font.Font(None, title_size)
        self.menu_font = pygame.font.Font(None, menu_size)
        self.subtitle_font = pygame.font.Font(None, subtitle_size)
    
    def handle_input(self):
        """Handle keyboard input for menu navigation."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                if not self.settings.fullscreen:
                    self.screen_width, self.screen_height = event.w, event.h
                    self.settings.window_size = (self.screen_width, self.screen_height)
                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                    # Update fonts for new screen size
                    title_size = UITheme.get_responsive_font_size(72, self.screen_height, 48)
                    menu_size = UITheme.get_responsive_font_size(48, self.screen_height, 32)
                    subtitle_size = UITheme.get_responsive_font_size(24, self.screen_height, 18)
                    self.title_font = pygame.font.Font(None, title_size)
                    self.menu_font = pygame.font.Font(None, menu_size)
                    self.subtitle_font = pygame.font.Font(None, subtitle_size)
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
                            result = callback()
                            # If game returns 'exit', quit the menu
                            if result == 'exit':
                                return False
                            # Otherwise continue menu (game returned 'main_menu' or None)
                        except SystemExit:
                            # Game exited, return to menu
                            pass
                        return True  # Continue menu after game
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def draw(self):
        """Draw the menu."""
        self.screen.fill(self.BLACK)
        
        # Title - responsive positioning
        title_text = self.title_font.render("67 Games", True, self.YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.1)))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.subtitle_font.render("Select a game using arrow keys and press ENTER", True, self.GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.15)))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Game list - responsive positioning with more spacing
        # Game list - responsive positioning with more spacing
        start_y = int(self.screen_height * 0.22)
        spacing = int(self.screen_height * 0.18)
        
        for i, (name, description, _) in enumerate(self.games):
            y_pos = start_y + i * spacing
            item_height = int(self.screen_height * 0.16)
            
            # Highlight selected game
            if i == self.selected_index:
                # Draw background highlight
                highlight_rect = pygame.Rect(
                    int(self.screen_width * 0.05), 
                    y_pos,
                    int(self.screen_width * 0.9), 
                    item_height
                )
                pygame.draw.rect(self.screen, self.DARK_BLUE, highlight_rect)
                pygame.draw.rect(self.screen, self.BLUE, highlight_rect, 3)
                
                # Draw selection arrow
                arrow_text = self.menu_font.render(">", True, self.YELLOW)
                arrow_y = y_pos + (item_height - arrow_text.get_height()) // 2
                self.screen.blit(arrow_text, (int(self.screen_width * 0.08), arrow_y))
            
            # Game name
            color = self.YELLOW if i == self.selected_index else self.WHITE
            name_text = self.menu_font.render(name, True, color)
            name_y = y_pos + int(item_height * 0.15)
            self.screen.blit(name_text, (int(self.screen_width * 0.12), name_y))
            
            # Description
            desc_text = self.subtitle_font.render(description, True, self.GRAY)
            desc_y = name_y + name_text.get_height() + 5 
            self.screen.blit(desc_text, (int(self.screen_width * 0.12), desc_y))
        
        # Instructions - responsive positioning
        if self.games:
            instructions = [
                "UP/DOWN: Navigate",
                "ENTER: Select game",
                "F11: Toggle Fullscreen",
                "ESC: Exit"
            ]
            y_offset = int(self.screen_height * 0.85)
            spacing = int(self.screen_height * 0.04)
            for i, instruction in enumerate(instructions):
                inst_text = self.subtitle_font.render(instruction, True, self.GRAY)
                self.screen.blit(inst_text, (int(self.screen_width * 0.05), y_offset + i * spacing))
        
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
