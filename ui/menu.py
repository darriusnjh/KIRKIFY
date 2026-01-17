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
        w, h = self.settings.window_size
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        self.screen_width, self.screen_height = w, h
        pygame.display.set_caption("67 Games")
        self.clock = pygame.time.Clock()
        self.bg_image = pygame.image.load("assets/background.png").convert()
        self.bg_cache_size = None
        self.bg_scaled = None
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
    def _get_scaled_bg(self):
        size = (self.screen_width, self.screen_height)
        if self.bg_cache_size != size:
            self.bg_scaled = pygame.transform.smoothscale(self.bg_image, size)
            self.bg_cache_size = size
        return self.bg_scaled

    def add_game(self, name: str, description: str, callback: Callable):
        """Add a game to the menu."""
        self.games.append((name, description, callback))
    
    
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
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def draw(self):
        """Draw the menu."""
        # Background image
        self.screen.blit(self._get_scaled_bg(), (0, 0))
        self.overlay_alpha = 170
        # Dark overlay for readability
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha))
        self.screen.blit(overlay, (0, 0))

        # ===== Title (with shadow) =====
        self.draw_text_shadow_center(
            self.title_font,
            "67 Games",
            self.YELLOW,
            (self.screen_width // 2, int(self.screen_height * 0.10)),
            offset=3
        )

        # ===== Subtitle (with shadow) =====
        self.draw_text_shadow_center(
            self.subtitle_font,
            "Select a game using arrow keys and press ENTER",
            self.WHITE,  # brighter than GRAY for busy backgrounds
            (self.screen_width // 2, int(self.screen_height * 0.15)),
            offset=2
        )

        # ===== Game list layout =====
        start_y = int(self.screen_height * 0.22)
        spacing = int(self.screen_height * 0.18)

        for i, (name, description, _) in enumerate(self.games):
            y_pos = start_y + i * spacing
            item_height = int(self.screen_height * 0.16)

            is_selected = (i == self.selected_index)

            # Bright-mode highlight card for selected item
            if is_selected:
                highlight_rect = pygame.Rect(
                    int(self.screen_width * 0.05),
                    y_pos,
                    int(self.screen_width * 0.9),
                    item_height
                )

                card = pygame.Surface((highlight_rect.w, highlight_rect.h), pygame.SRCALPHA)
                card.fill((245, 248, 255, 210))  # light card
                self.screen.blit(card, (highlight_rect.x, highlight_rect.y))

                pygame.draw.rect(self.screen, (90, 140, 255), highlight_rect, 4)

                arrow_text = self.menu_font.render(">", True, (20, 20, 20))
                arrow_y = y_pos + (item_height - arrow_text.get_height()) // 2
                self.screen.blit(arrow_text, (int(self.screen_width * 0.08), arrow_y))

            # Text colors (dark on light card, light on dark background)
            name_color = (25, 25, 25) if is_selected else self.WHITE
            desc_color = (60, 60, 60) if is_selected else self.GRAY

            name_x = int(self.screen_width * 0.12)
            name_y = y_pos + int(item_height * 0.15)

            # Game name (with shadow; smaller shadow on selected)
            self.draw_text_shadow(
                self.menu_font,
                name,
                name_color,
                (name_x, name_y),
                shadow_color=(0, 0, 0) if not is_selected else (255, 255, 255),
                offset=2 if not is_selected else 1
            )

            # Description (with shadow)
            desc_y = name_y + self.menu_font.get_height() + 5
            self.draw_text_shadow(
                self.subtitle_font,
                description,
                desc_color,
                (name_x, desc_y),
                shadow_color=(0, 0, 0) if not is_selected else (255, 255, 255),
                offset=1
            )

        # ===== Instructions (with shadow) =====
        if self.games:
            instructions = [
                "UP/DOWN: Navigate",
                "ENTER: Select game",
                "ESC: Exit"
            ]
            x = int(self.screen_width * 0.05)
            y_offset = int(self.screen_height * 0.85)
            inst_spacing = int(self.screen_height * 0.04)

            for idx, instruction in enumerate(instructions):
                self.draw_text_shadow(
                    self.subtitle_font,
                    instruction,
                    self.WHITE,  # brighter
                    (x, y_offset + idx * inst_spacing),
                    offset=2
                )

        pygame.display.flip()

    def draw_text_shadow(
        self,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        pos: tuple[int, int],
        shadow_color: tuple[int, int, int] = (0, 0, 0),
        offset: int = 2
    ) -> pygame.Rect:
        x, y = pos

        shadow_surf = font.render(text, True, shadow_color)
        self.screen.blit(shadow_surf, (x + offset, y + offset))

        text_surf = font.render(text, True, color)
        rect = text_surf.get_rect(topleft=(x, y))
        self.screen.blit(text_surf, rect)
        return rect

    
    def draw_text_shadow_center(
        self,
        font: pygame.font.Font,
        text: str,
        color: tuple[int, int, int],
        center: tuple[int, int],
        shadow_color: tuple[int, int, int] = (0, 0, 0),
        offset: int = 2
    ) -> pygame.Rect:
        shadow_surf = font.render(text, True, shadow_color)
        shadow_rect = shadow_surf.get_rect(center=(center[0] + offset, center[1] + offset))
        self.screen.blit(shadow_surf, shadow_rect)

        text_surf = font.render(text, True, color)
        rect = text_surf.get_rect(center=center)
        self.screen.blit(text_surf, rect)
        return rect

    def run(self):
        """Run the menu loop."""
        while self.running:
            if not self.handle_input():
                break
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    