"""
UI Utilities for consistent, modern UI across all games.
"""
import pygame


class UITheme:
    """Modern, minimalistic UI theme."""
    
    # Dark theme colors
    BG_DARK = (18, 18, 23)
    BG_LIGHT = (28, 28, 35)
    ACCENT_PRIMARY = (99, 102, 241)  # Indigo
    ACCENT_SECONDARY = (139, 92, 246)  # Purple
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (161, 161, 170)
    TEXT_HIGHLIGHT = (255, 255, 255)
    SUCCESS = (34, 197, 94)
    WARNING = (251, 191, 36)
    ERROR = (239, 68, 68)
    
    @staticmethod
    def get_responsive_font_size(base_size: int, screen_height: int, min_size: int = 12) -> int:
        """Calculate responsive font size based on screen height."""
        return max(min_size, int(base_size * (screen_height / 600)))
    
    @staticmethod
    def create_screen(fullscreen: bool = False, width: int = None, height: int = None):
        """Create a pygame screen with fullscreen support."""
        display_info = pygame.display.Info()
        
        if fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            return screen, screen.get_size()
        else:
            if width is None:
                width = min(1920, display_info.current_w)
            if height is None:
                height = min(1080, display_info.current_h)
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            return screen, (width, height)
    
    @staticmethod
    def draw_text_with_shadow(surface, text, font, color, pos, shadow_color=(0, 0, 0), shadow_offset=2):
        """Draw text with a shadow effect for better readability."""
        shadow_surf = font.render(text, True, shadow_color)
        text_surf = font.render(text, True, color)
        surface.blit(shadow_surf, (pos[0] + shadow_offset, pos[1] + shadow_offset))
        surface.blit(text_surf, pos)
        return text_surf.get_rect(topleft=pos)
    
    @staticmethod
    def draw_rounded_rect(surface, color, rect, border_radius=0, border_width=0, border_color=None):
        """Draw a rounded rectangle."""
        if border_radius == 0:
            if border_width > 0 and border_color:
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, border_color, rect, border_width)
            else:
                pygame.draw.rect(surface, color, rect)
        else:
            # Simple rounded rect approximation
            pygame.draw.rect(surface, color, rect, border_radius=border_radius)
            if border_width > 0 and border_color:
                pygame.draw.rect(surface, border_color, rect, border_width, border_radius=border_radius)
