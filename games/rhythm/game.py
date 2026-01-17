import pygame
import random
import sys
import time
from typing import List, Optional
from core.sound_manager import SoundManager
# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
GRAY = (100, 100, 100)
PURPLE = (200, 100, 255)

# Game settings
NOTE_WIDTH = 80
NOTE_HEIGHT = 30
NOTE_SPEED = 5
HIT_ZONE_Y = 500
HIT_ZONE_HEIGHT = 60
SPAWN_INTERVAL = 30  # frames between notes
LEFT_LANE_X = 250
RIGHT_LANE_X = 550

# Timing windows (in pixels from hit zone)
PERFECT_WINDOW = 20
GOOD_WINDOW = 40
OK_WINDOW = 60


class Note:
    def __init__(self, lane: str, y: float = 0):
        """
        Create a note that falls down the screen.
        
        Args:
            lane: 'Left' or 'Right'
            y: Starting Y position
        """
        self.lane = lane
        self.y = y
        self.x = LEFT_LANE_X if lane == 'Left' else RIGHT_LANE_X
        self.width = NOTE_WIDTH
        self.height = NOTE_HEIGHT
        self.active = True
        self.hit = False
        
    def update(self):
        """Move note downward."""
        self.y += NOTE_SPEED
        
        # Deactivate if past screen
        if self.y > SCREEN_HEIGHT + 50:
            self.active = False
            
    def draw(self, screen):
        """Draw the note."""
        if not self.active:
            return
            
        color = BLUE if self.lane == 'Left' else RED
        
        # Draw note rectangle
        rect = pygame.Rect(self.x - self.width // 2, int(self.y), self.width, self.height)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)
        
        # Draw hand indicator
        font = pygame.font.Font(None, 24)
        text = "👈 L" if self.lane == 'Left' else "R 👉"
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x, int(self.y) + self.height // 2))
        screen.blit(text_surface, text_rect)
        
    def get_distance_from_hit_zone(self) -> float:
        """Get distance from center of hit zone."""
        return abs(self.y - HIT_ZONE_Y)


class RhythmGame:
    def __init__(self, fullscreen: bool = False):
        self.fullscreen = fullscreen
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Rhythm Hand Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.webcam_surface = None  # For external webcam feed
        self.detected_hands_info = []  # For hand detection info
        self.sound_manager = SoundManager()
        self.reset()
        
    def reset(self):
        """Reset game state."""
        self.notes: List[Note] = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.perfect_hits = 0
        self.good_hits = 0
        self.ok_hits = 0
        self.misses = 0
        self.frame_count = 0
        self.game_over = False
        self.game_started = False
        self.last_hit_hand = None
        self.feedback_text = ""
        self.feedback_timer = 0
        self.notes_spawned = 0
        self.max_notes = 50  # Total notes in the game
        
    def spawn_note(self):
        """Spawn a new note in random lane."""
        lane = random.choice(['Left', 'Right'])
        self.notes.append(Note(lane))
        self.notes_spawned += 1
        
    def check_hit(self, hand: str) -> Optional[str]:
        """
        Check if a hand gesture hits a note.
        
        Args:
            hand: 'Left' or 'Right'
            
        Returns:
            Hit quality: 'perfect', 'good', 'ok', or None
        """
        # Find closest active note in matching lane
        matching_notes = [n for n in self.notes if n.active and not n.hit and n.lane == hand]
        
        if not matching_notes:
            return None
            
        # Get closest note to hit zone
        closest_note = min(matching_notes, key=lambda n: n.get_distance_from_hit_zone())
        distance = closest_note.get_distance_from_hit_zone()
        
        # Check timing windows
        if distance <= PERFECT_WINDOW:
            closest_note.hit = True
            closest_note.active = False
            self.perfect_hits += 1
            self.score += 100
            self.combo += 1
            return 'perfect'
        elif distance <= GOOD_WINDOW:
            closest_note.hit = True
            closest_note.active = False
            self.good_hits += 1
            self.score += 50
            self.combo += 1
            return 'good'
        elif distance <= OK_WINDOW:
            closest_note.hit = True
            closest_note.active = False
            self.ok_hits += 1
            self.score += 25
            self.combo += 1
            return 'ok'
            
        return None
        
    def check_missed_notes(self):
        """Check for notes that passed the hit zone."""
        for note in self.notes:
            if note.active and not note.hit and note.y > HIT_ZONE_Y + OK_WINDOW + 20:
                note.active = False
                self.misses += 1
                self.combo = 0
                self.show_feedback("MISS!", RED)
                
    def show_feedback(self, text: str, color):
        """Show feedback text."""
        self.feedback_text = text
        self.feedback_color = color
        self.feedback_timer = 30  # frames
        
    def handle_hand_gesture(self, hand: str):
        """
        Handle a hand gesture (left or right wave).
        
        Args:
            hand: 'Left' or 'Right'
        """
        if not self.game_started:
            self.game_started = True
            if self.sound_manager:
                self.sound_manager.start_background_music("rhythmsound.mp3") 
            return
            
        if self.game_over:
            return
            
        hit_quality = self.check_hit(hand)
        
        if hit_quality == 'perfect':
            self.show_feedback("PERFECT!", YELLOW)
        elif hit_quality == 'good':
            self.show_feedback("GOOD!", GREEN)
        elif hit_quality == 'ok':
            self.show_feedback("OK", WHITE)
        else:
            # Gesture but no note to hit
            self.combo = 0
            
        self.last_hit_hand = hand
        
        # Update max combo
        if self.combo > self.max_combo:
            self.max_combo = self.combo
            
    def update(self):
        """Update game state."""
        if not self.game_started or self.game_over:
            return
            
        self.frame_count += 1
        
        # Spawn notes
        if self.frame_count % SPAWN_INTERVAL == 0 and self.notes_spawned < self.max_notes:
            self.spawn_note()
            
        # Update notes
        for note in self.notes:
            note.update()
            
        # Check for missed notes
        self.check_missed_notes()
        
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            
        # Check if game is over (all notes spawned and all gone)
        if self.notes_spawned >= self.max_notes:
            active_notes = [n for n in self.notes if n.active]
            if len(active_notes) == 0:
                self.game_over = True
                
    def draw(self):
        """Draw everything."""
        # Background
        self.screen.fill(BLACK)
        
        # Draw lanes
        lane_color = (50, 50, 50)
        pygame.draw.rect(self.screen, lane_color, 
                        (LEFT_LANE_X - NOTE_WIDTH // 2 - 10, 0, NOTE_WIDTH + 20, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, lane_color,
                        (RIGHT_LANE_X - NOTE_WIDTH // 2 - 10, 0, NOTE_WIDTH + 20, SCREEN_HEIGHT))
        
        # Draw lane labels at top
        left_label = self.font.render("👈 LEFT", True, BLUE)
        right_label = self.font.render("RIGHT 👉", True, RED)
        self.screen.blit(left_label, (LEFT_LANE_X - 50, 20))
        self.screen.blit(right_label, (RIGHT_LANE_X - 60, 20))
        
        # Draw hit zone
        hit_zone_rect = pygame.Rect(0, HIT_ZONE_Y - HIT_ZONE_HEIGHT // 2, 
                                    SCREEN_WIDTH, HIT_ZONE_HEIGHT)
        pygame.draw.rect(self.screen, (100, 100, 0, 128), hit_zone_rect)
        pygame.draw.line(self.screen, YELLOW, (0, HIT_ZONE_Y), (SCREEN_WIDTH, HIT_ZONE_Y), 3)
        
        # Draw notes
        for note in self.notes:
            note.draw(self.screen)
            
        # Draw UI
        self.draw_ui()
        
        # Draw start screen
        if not self.game_started:
            self.draw_start_screen()
            
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        
        # Draw webcam feed if available
        self.draw_webcam_overlay()
            
        pygame.display.flip()
        
    def draw_ui(self):
        """Draw UI elements."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Combo
        if self.combo > 0:
            combo_text = self.font.render(f"Combo: {self.combo}x", True, YELLOW)
            self.screen.blit(combo_text, (10, 50))
            
        # Stats
        stats_y = 90
        stats = [
            f"Perfect: {self.perfect_hits}",
            f"Good: {self.good_hits}",
            f"OK: {self.ok_hits}",
            f"Miss: {self.misses}"
        ]
        for stat in stats:
            stat_text = self.small_font.render(stat, True, GRAY)
            self.screen.blit(stat_text, (10, stats_y))
            stats_y += 25
            
        # Progress
        progress = f"Notes: {self.notes_spawned}/{self.max_notes}"
        progress_text = self.small_font.render(progress, True, WHITE)
        self.screen.blit(progress_text, (SCREEN_WIDTH - 150, 10))
        
        # Feedback
        if self.feedback_timer > 0:
            feedback = self.big_font.render(self.feedback_text, True, self.feedback_color)
            feedback_rect = feedback.get_rect(center=(SCREEN_WIDTH // 2, 200))
            self.screen.blit(feedback, feedback_rect)
            
    def draw_start_screen(self):
        """Draw start screen overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.big_font.render("RHYTHM HAND GAME", True, PURPLE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "Wave hands to hit the notes!",
            "👈 LEFT hand for BLUE notes",
            "RIGHT hand 👉 for RED notes",
            "",
            "Hit notes at the YELLOW line",
            "for maximum points!",
            "",
            "Wave either hand to start!"
        ]
        
        y = 250
        for line in instructions:
            text = self.font.render(line, True, WHITE) if line else None
            if text:
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
            y += 35
            
    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.big_font.render("GAME OVER!", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Calculate accuracy
        total_notes = self.perfect_hits + self.good_hits + self.ok_hits + self.misses
        accuracy = 0 if total_notes == 0 else ((self.perfect_hits + self.good_hits + self.ok_hits) / total_notes) * 100
        
        results = [
            f"Final Score: {self.score}",
            f"Max Combo: {self.max_combo}x",
            f"Accuracy: {accuracy:.1f}%",
            "",
            f"Perfect: {self.perfect_hits}",
            f"Good: {self.good_hits}",
            f"OK: {self.ok_hits}",
            f"Miss: {self.misses}",
            "",
            "Press R to Restart",
            "Press ESC to Quit"
        ]
        
        y = 200
        for line in results:
            color = WHITE if line else BLACK
            text = self.font.render(line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 40
    
    def set_webcam_surface(self, surface):
        """Set the webcam surface to display."""
        self.webcam_surface = surface
    
    def set_detected_hands(self, hands_info):
        """Set detected hands info."""
        self.detected_hands_info = hands_info
    
    def draw_webcam_overlay(self):
        """Draw webcam feed and hand detection info."""
        # Draw webcam feed
        if self.webcam_surface:
            # Scale webcam feed
            target_width = 240
            target_height = 180
            scaled_surface = pygame.transform.scale(self.webcam_surface, (target_width, target_height))
            
            # Position in bottom-right corner
            x_pos = SCREEN_WIDTH - target_width - 10
            y_pos = SCREEN_HEIGHT - target_height - 10
            
            # Draw webcam feed
            self.screen.blit(scaled_surface, (x_pos, y_pos))
            
            # Draw border
            border_rect = pygame.Rect(x_pos, y_pos, target_width, target_height)
            pygame.draw.rect(self.screen, WHITE, border_rect, 3)
            
            # Draw label
            label_font = pygame.font.Font(None, 20)
            label = label_font.render("Webcam", True, WHITE)
            label_bg = pygame.Surface((label.get_width() + 10, label.get_height() + 4))
            label_bg.fill(BLACK)
            label_bg.set_alpha(180)
            self.screen.blit(label_bg, (x_pos, y_pos - 25))
            self.screen.blit(label, (x_pos + 5, y_pos - 23))
        
        # Draw hand detection status
        if self.detected_hands_info:
            hand_font = pygame.font.Font(None, 24)
            y_offset = 300
            
            for hand in self.detected_hands_info:
                handedness = hand.get('handedness', 'Unknown')
                confidence = hand.get('confidence', 0)
                
                if handedness == 'Left':
                    color = (100, 150, 255)
                    text = f"👈 Left: {confidence:.0%}"
                    self.screen.blit(hand_font.render(text, True, color), (10, y_offset))
                elif handedness == 'Right':
                    color = (255, 100, 100)
                    text = f"Right: {confidence:.0%} 👉"
                    text_surface = hand_font.render(text, True, color)
                    text_rect = text_surface.get_rect(right=SCREEN_WIDTH - 10, top=y_offset)
                    self.screen.blit(text_surface, text_rect)
                
                y_offset += 30
            
    def run(self):
        """Main game loop (keyboard only)."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
                    elif event.key == pygame.K_a:  # Left hand (for testing)
                        self.handle_hand_gesture('Left')
                    elif event.key == pygame.K_l:  # Right hand (for testing)
                        self.handle_hand_gesture('Right')
                        
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = RhythmGame()
    game.run()

