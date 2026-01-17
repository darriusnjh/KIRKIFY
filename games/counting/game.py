import pygame
import json
import os
import time
import sys
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from core.base_game import BaseGame


class CountingGame(BaseGame):
    """Counting game: Count alternating hand gestures in 30 seconds."""
    
    def __init__(self, sound_manager=None, screen_width=800, screen_height=600):
        super().__init__(sound_manager)
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Game state
        self.count = 0
        self.time_remaining = 30.0  # 30 seconds
        self.last_completed_hand = None  # 'left' or 'right' or None - tracks which hand last completed a cycle
        self.game_start_time = None
        
        # Hand movement states: 'idle', 'moving_up', 'moving_down', 'completed'
        self.hand_states = {'left': 'idle', 'right': 'idle'}
        
        # High score
        self.high_score = self.load_high_score()
        
        # Webcam feed
        self.webcam_surface = None
        
        # Fonts (will be updated responsively)
        self.update_fonts()
        
        # Modern color palette
        from core.ui_utils import UITheme
        self.theme = UITheme
        self.BG_DARK = UITheme.BG_DARK
        self.TEXT_PRIMARY = UITheme.TEXT_PRIMARY
        self.TEXT_SECONDARY = UITheme.TEXT_SECONDARY
        self.ACCENT_PRIMARY = UITheme.ACCENT_PRIMARY
        self.ACCENT_SECONDARY = UITheme.ACCENT_SECONDARY
        self.SUCCESS = UITheme.SUCCESS
        self.WARNING = UITheme.WARNING
        self.ERROR = UITheme.ERROR
        
        # Legacy colors for compatibility
        self.WHITE = self.TEXT_PRIMARY
        self.BLACK = self.BG_DARK
        self.BLUE = self.ACCENT_PRIMARY
        self.RED = self.ERROR
        self.GREEN = self.SUCCESS
        self.YELLOW = self.WARNING
        self.ORANGE = (255, 165, 0)
        self.GRAY = self.TEXT_SECONDARY
    
    def update_fonts(self):
        """Update fonts based on current screen size."""
        from core.ui_utils import UITheme
        self.big_font_size = UITheme.get_responsive_font_size(120, self.screen_height, 60)
        self.medium_font_size = UITheme.get_responsive_font_size(72, self.screen_height, 36)
        self.small_font_size = UITheme.get_responsive_font_size(36, self.screen_height, 18)
        
        self.big_font = pygame.font.Font(None, self.big_font_size)
        self.medium_font = pygame.font.Font(None, self.medium_font_size)
        self.small_font = pygame.font.Font(None, self.small_font_size)
        
    def load_high_score(self):
        """Load high score from file."""
        try:
            if os.path.exists('high_scores.json'):
                with open('high_scores.json', 'r') as f:
                    data = json.load(f)
                    return data.get('counting_game', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        """Save high score to file."""
        try:
            data = {}
            if os.path.exists('high_scores.json'):
                with open('high_scores.json', 'r') as f:
                    data = json.load(f)
            
            data['counting_game'] = self.high_score
            
            with open('high_scores.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def reset(self):
        """Reset game state."""
        super().reset()
        self.count = 0
        self.time_remaining = 30.0
        self.last_completed_hand = None
        self.game_start_time = None
        self.hand_states = {'left': 'idle', 'right': 'idle'}
    
    def start_game(self):
        """Start the counting game."""
        self.game_started = True
        self.game_start_time = time.time()
        if self.sound_manager:
            self.sound_manager.play_start_sound()
    
    def handle_action(self, action: str):
        """
        Handle hand movement action.
        Actions: 'left_up', 'left_down', 'right_up', 'right_down'
        Counts when a complete up-down cycle is completed and alternates with previous hand.
        """
        if not self.game_started:
            self.start_game()
            return
        
        if self.game_over:
            return
        
        # Parse action into hand and direction
        if '_' not in action:
            return
        
        hand, direction = action.split('_')
        
        if hand not in ['left', 'right'] or direction not in ['up', 'down']:
            return
        
        current_state = self.hand_states[hand]
        
        # State machine for detecting complete cycles (up then down)
        if direction == 'up':
            if current_state == 'idle' or current_state == 'moving_down':
                # Hand started moving up (or restarted after going down)
                self.hand_states[hand] = 'moving_up'
        
        elif direction == 'down':
            if current_state == 'moving_up':
                # Hand completed up-down cycle! (went up, now going down)
                # Check if this hand alternates with the last completed hand
                if self.last_completed_hand != hand:
                    # Valid alternating cycle - count it!
                    self.count += 1
                    self.last_completed_hand = hand
                    
                    if self.sound_manager:
                        # Play the 67.m4a sound when count increases
                        self.sound_manager.play_count_sound()
                    
                    # Update high score
                    if self.count > self.high_score:
                        self.high_score = self.count
                        self.save_high_score()
                    
                    # Reset this hand's state to idle for next cycle
                    self.hand_states[hand] = 'idle'
                else:
                    # Same hand as last time - don't count, but reset state
                    self.hand_states[hand] = 'idle'
            elif current_state == 'idle':
                # Hand started moving down (without going up first) - ignore
                pass
    
    def update(self):
        """Update game state."""
        if not self.game_started or self.game_over:
            return
        
        # Update timer
        if self.game_start_time:
            elapsed = time.time() - self.game_start_time
            self.time_remaining = max(0, 30.0 - elapsed)
            
            # Game over when time runs out
            if self.time_remaining <= 0:
                self.game_over = True
                if self.sound_manager:
                    self.sound_manager.play_hit_sound()
    
    def draw(self):
        """Draw the game."""
        if not self.screen:
            return
        
        # Modern gradient background
        self.screen.fill(self.BG_DARK)
        
        # Subtle gradient effect
        for y in range(0, self.screen_height, 2):
            alpha = int(255 * (1 - y / self.screen_height * 0.3))
            color = tuple(min(255, c + int((self.BG_DARK[0] - c) * y / self.screen_height)) for c in self.BG_DARK)
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))
        
        if not self.game_started:
            # Start screen
            title_text = self.big_font.render("Counting Game", True, self.YELLOW)
            title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
            self.screen.blit(title_text, title_rect)
            
            instruction_text = self.medium_font.render("Move hands UP and DOWN alternately!", True, self.WHITE)
            inst_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(instruction_text, inst_rect)
            
            start_text = self.small_font.render("Wave your hand to start!", True, self.GREEN)
            start_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 80))
            self.screen.blit(start_text, start_rect)
            
            high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, self.GRAY)
            hs_rect = high_score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 130))
            self.screen.blit(high_score_text, hs_rect)
            
            # Draw webcam feed if available (on start screen too)
            if self.webcam_surface:
                cam_width = int(self.screen_width * 0.3)
                cam_height = int(cam_width * 0.75)
                scaled_surface = pygame.transform.scale(self.webcam_surface, (cam_width, cam_height))
                
                cam_x = self.screen_width - cam_width - 20
                cam_y = self.screen_height - cam_height - 20
                
                # Draw border
                border_thickness = 3
                pygame.draw.rect(self.screen, self.WHITE, 
                               (cam_x - border_thickness, cam_y - border_thickness, 
                                cam_width + border_thickness * 2, cam_height + border_thickness * 2), 
                               border_thickness)
                
                self.screen.blit(scaled_surface, (cam_x, cam_y))
                
                # Add label
                label_text = self.small_font.render("Camera Feed", True, self.WHITE)
                label_rect = label_text.get_rect(center=(cam_x + cam_width // 2, cam_y - 20))
                self.screen.blit(label_text, label_rect)
            
        elif self.game_over:
            # Game over screen
            game_over_text = self.big_font.render("TIME'S UP!", True, self.RED)
            go_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 150))
            self.screen.blit(game_over_text, go_rect)
            
            count_text = self.medium_font.render(f"Count: {self.count}", True, self.WHITE)
            count_rect = count_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.screen.blit(count_text, count_rect)
            
            high_score_text = self.medium_font.render(f"High Score: {self.high_score}", True, self.YELLOW)
            hs_rect = high_score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
            self.screen.blit(high_score_text, hs_rect)
            
            restart_text = self.small_font.render("Press R to restart or ESC to return to menu", True, self.GRAY)
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
            self.screen.blit(restart_text, restart_rect)
            
            # Draw webcam feed if available (on game over screen too)
            if self.webcam_surface:
                cam_width = int(self.screen_width * 0.3)
                cam_height = int(cam_width * 0.75)
                scaled_surface = pygame.transform.scale(self.webcam_surface, (cam_width, cam_height))
                
                cam_x = self.screen_width - cam_width - 20
                cam_y = self.screen_height - cam_height - 20
                
                # Draw border
                border_thickness = 3
                pygame.draw.rect(self.screen, self.WHITE, 
                               (cam_x - border_thickness, cam_y - border_thickness, 
                                cam_width + border_thickness * 2, cam_height + border_thickness * 2), 
                               border_thickness)
                
                self.screen.blit(scaled_surface, (cam_x, cam_y))
                
                # Add label
                label_text = self.small_font.render("Camera Feed", True, self.WHITE)
                label_rect = label_text.get_rect(center=(cam_x + cam_width // 2, cam_y - 20))
                self.screen.blit(label_text, label_rect)
            
        else:
            # Game in progress
            # Count display (big and centered)
            count_text = self.big_font.render(str(self.count), True, self.GREEN)
            count_rect = count_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.screen.blit(count_text, count_rect)
            
            # Timer (top center)
            timer_text = self.medium_font.render(f"{self.time_remaining:.1f}", True, self.YELLOW)
            timer_rect = timer_text.get_rect(center=(self.screen_width // 2, 50))
            self.screen.blit(timer_text, timer_rect)
            
            # Instructions
            if self.last_completed_hand is None:
                instruction_text = self.small_font.render("Move either hand UP then DOWN to start!", True, self.WHITE)
            elif self.last_completed_hand == 'left':
                instruction_text = self.small_font.render("Move RIGHT hand UP then DOWN! 👉", True, self.RED)
            else:  # last_completed_hand == 'right'
                instruction_text = self.small_font.render("Move LEFT hand UP then DOWN! 👈", True, self.BLUE)
            
            # Show current hand states
            left_state = self.hand_states['left']
            right_state = self.hand_states['right']
            state_text = self.small_font.render(
                f"L:{left_state[:4]} R:{right_state[:4]}", 
                True, self.GRAY
            )
            self.screen.blit(state_text, (50, self.screen_height - 80))
            
            inst_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
            self.screen.blit(instruction_text, inst_rect)
            
            # High score (top right)
            hs_text = self.small_font.render(f"Best: {self.high_score}", True, self.GRAY)
            self.screen.blit(hs_text, (self.screen_width - 200, 20))
            
            # Progress bar
            progress = (30.0 - self.time_remaining) / 30.0
            bar_width = self.screen_width - 200
            bar_height = 10
            bar_x = 100
            bar_y = self.screen_height - 50
            
            # Background bar
            pygame.draw.rect(self.screen, self.GRAY, (bar_x, bar_y, bar_width, bar_height))
            # Progress bar
            if progress > 0:
                color = self.GREEN if progress < 0.7 else (self.ORANGE if progress < 0.9 else self.RED)
                pygame.draw.rect(self.screen, color, (bar_x, bar_y, int(bar_width * progress), bar_height))
            
            # Draw webcam feed if available
            if self.webcam_surface:
                # Scale to reasonable size (e.g., 25% of screen width)
                cam_width = int(self.screen_width * 0.3)
                cam_height = int(cam_width * 0.75)  # 4:3 aspect ratio
                scaled_surface = pygame.transform.scale(self.webcam_surface, (cam_width, cam_height))
                
                # Position in bottom-right corner with some padding
                cam_x = self.screen_width - cam_width - 20
                cam_y = self.screen_height - cam_height - 80  # Above progress bar
                
                # Draw border around camera feed
                border_thickness = 3
                pygame.draw.rect(self.screen, self.WHITE, 
                               (cam_x - border_thickness, cam_y - border_thickness, 
                                cam_width + border_thickness * 2, cam_height + border_thickness * 2), 
                               border_thickness)
                
                # Draw camera feed
                self.screen.blit(scaled_surface, (cam_x, cam_y))
                
                # Add label
                label_text = self.small_font.render("Camera Feed", True, self.WHITE)
                label_rect = label_text.get_rect(center=(cam_x + cam_width // 2, cam_y - 20))
                self.screen.blit(label_text, label_rect)
        
        pygame.display.flip()
    
    def get_score(self) -> int:
        """Get current count."""
        return self.count
    
    def get_high_score_key(self) -> str:
        """Get the key for storing high score."""
        return "counting_game"
    
    def set_webcam_frame(self, surface):
        """Set the webcam frame surface to display."""
        self.webcam_surface = surface
