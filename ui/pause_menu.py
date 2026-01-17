"""Pause menu for in-game navigation."""
import pygame
import sys
from typing import Optional
from core.ui_utils import UITheme
from core.sound_manager import SoundManager

class PauseMenu:
    """In-game pause menu with options to resume, return to main menu, or exit."""
    
    def __init__(self, screen, screen_width: int, screen_height: int):
        """
        Initialize pause menu.
        
        Args:
            screen: Pygame screen surface
            screen_width: Screen width
            screen_height: Screen height
        """
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sound_manager = SoundManager()

        # Calculate responsive font sizes
        self.title_font_size = UITheme.get_responsive_font_size(64, screen_height, 48)
        self.menu_font_size = UITheme.get_responsive_font_size(36, screen_height, 28)
        self.subtitle_font_size = UITheme.get_responsive_font_size(24, screen_height, 18)
        
        self.title_font = pygame.font.Font(None, self.title_font_size)
        self.menu_font = pygame.font.Font(None, self.menu_font_size)
        self.subtitle_font = pygame.font.Font(None, self.subtitle_font_size)
        
        # Menu state
        self.selected_index = 0
        self.options = [
            ("Resume", "Continue playing"),
            ("Main Menu", "Return to game selection"),
            ("Exit", "Quit the game")
        ]
        self.running = True
        self.result = None  # 'resume', 'main_menu', or 'exit'
    
    def handle_input(self):
        """Handle keyboard input for pause menu."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.result = 'exit'
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Select option
                    option_name = self.options[self.selected_index][0]
                    if option_name == "Resume":
                        self.result = 'resume'
                    elif option_name == "Main Menu":
                        if self.sound_manager:
                            self.sound_manager.stop_all_sounds()
                        self.result = 'main_menu'
                    elif option_name == "Exit":
                        if self.sound_manager:
                            self.sound_manager.stop_all_sounds()
                        self.result = 'exit'
                    return False
                elif event.key == pygame.K_ESCAPE:
                    # ESC also resumes
                    self.result = 'resume'
                    return False
        return True
    
    def draw(self, background_surface=None):
        """
        Draw the pause menu overlay.
        
        Args:
            background_surface: Optional background to show behind menu (blurred game screen)
        """
        # Draw background first if provided
        if background_surface is not None:
            self.screen.blit(background_surface, (0, 0))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(UITheme.BG_DARK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = self.title_font.render("PAUSED", True, UITheme.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.25)))
        
        # Add glow effect
        for i in range(3, 0, -1):
            glow_surface = self.title_font.render("PAUSED", True, (*UITheme.ACCENT_PRIMARY, 30 // i))
            glow_rect = glow_surface.get_rect(center=(self.screen_width // 2 + i, int(self.screen_height * 0.25) + i))
            self.screen.blit(glow_surface, glow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Draw menu options
        menu_start_y = int(self.screen_height * 0.4)
        option_spacing = int(self.screen_height * 0.1)
        
        for i, (name, description) in enumerate(self.options):
            y_pos = menu_start_y + i * option_spacing
            
            # Calculate card position
            is_selected = i == self.selected_index
            card_width = min(400, int(self.screen_width * 0.5))
            card_height = int(self.screen_height * 0.08)
            card_x = (self.screen_width - card_width) // 2
            
            # Draw option card
            card_rect = pygame.Rect(card_x, y_pos, card_width, card_height)
            
            if is_selected:
                pygame.draw.rect(self.screen, UITheme.ACCENT_PRIMARY, card_rect)
                pygame.draw.rect(self.screen, UITheme.ACCENT_SECONDARY, card_rect, width=2)
            else:
                pygame.draw.rect(self.screen, UITheme.BG_LIGHT, card_rect)
                pygame.draw.rect(self.screen, UITheme.TEXT_SECONDARY, card_rect, width=1)
            
            # Option name
            name_color = UITheme.TEXT_HIGHLIGHT if is_selected else UITheme.TEXT_PRIMARY
            name_text = self.menu_font.render(name, True, name_color)
            name_x = card_x + 20
            name_y = y_pos + 10
            self.screen.blit(name_text, (name_x, name_y))
            
            # Description
            desc_text = self.subtitle_font.render(description, True, UITheme.TEXT_SECONDARY)
            desc_x = card_x + 20
            desc_y = y_pos + card_height - 25
            self.screen.blit(desc_text, (desc_x, desc_y))
            
            # Selection indicator
            if is_selected:
                indicator_x = card_x - 30
                indicator_y = y_pos + card_height // 2
                pygame.draw.circle(self.screen, UITheme.ACCENT_PRIMARY, (indicator_x, indicator_y), 6)
                pygame.draw.circle(self.screen, UITheme.TEXT_PRIMARY, (indicator_x, indicator_y), 4)
        
        # Instructions
        instructions_y = int(self.screen_height * 0.85)
        instructions = [
            "↑↓ Navigate  •  ENTER Select  •  ESC Resume"
        ]
        for instruction in instructions:
            inst_text = self.subtitle_font.render(instruction, True, UITheme.TEXT_SECONDARY)
            inst_rect = inst_text.get_rect(center=(self.screen_width // 2, instructions_y))
            self.screen.blit(inst_text, inst_rect)
        
        pygame.display.flip()
    
    def run(self, background_surface=None):
        """
        Run the pause menu loop.
        
        Args:
            background_surface: Optional background to show behind menu
        
        Returns:
            'resume', 'main_menu', or 'exit'
        """
        clock = pygame.time.Clock()
        self.running = True  # Reset running state
        self.result = None  # Reset result
        
        while self.running:
            if not self.handle_input():
                break
            
            self.draw(background_surface)
            clock.tick(60)
        
        return self.result or 'resume'
