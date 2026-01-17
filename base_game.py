from abc import ABC, abstractmethod
from typing import Optional
import pygame


class BaseGame(ABC):
    """Base class for all games in 67 Games."""
    
    def __init__(self, sound_manager=None):
        self.sound_manager = sound_manager
        self.game_over = False
        self.game_started = False
        self.screen = None
        
    def set_screen(self, screen):
        """Set the pygame screen for drawing."""
        self.screen = screen
    
    @abstractmethod
    def update(self):
        """Update game state. Called every frame."""
        pass
    
    @abstractmethod
    def draw(self):
        """Draw game to screen. Called every frame."""
        pass
    
    @abstractmethod
    def handle_action(self, action: str):
        """Handle game action (e.g., 'jump', 'left', 'right', etc.)."""
        pass
    
    def reset(self):
        """Reset game state."""
        self.game_over = False
        self.game_started = False
    
    def get_score(self) -> int:
        """Get current game score."""
        return 0
    
    def get_high_score_key(self) -> str:
        """Get the key for storing high score in JSON."""
        return "default"
