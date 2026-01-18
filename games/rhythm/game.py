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
LONG_NOTE_HEIGHT = 200  # Long notes are taller
NOTE_SPEED = 7.5  # Increased by 50% (was 5)
HIT_ZONE_Y = 500
HIT_ZONE_HEIGHT = 60
SPAWN_INTERVAL = 30  # frames between notes
FEVER_SPAWN_INTERVAL = 15  # frames between notes during fever mode
LEFT_LANE_X = 250
RIGHT_LANE_X = 550
LONG_NOTE_CHANCE = 0.15  # 15% chance to spawn a long note

# Timing windows (in pixels from hit zone)
PERFECT_WINDOW = 20
GOOD_WINDOW = 40
OK_WINDOW = 60

# Long note settings
LONG_NOTE_HIT_COOLDOWN = 4  # Frames between hits on long note (for rapid tapping) - reduced for better responsiveness
LONG_NOTE_POINTS_PER_HIT = 20  # Points per rapid hit on long note

# Fever mode section settings
FEVER_MODE_DURATION = 300  # frames (5 seconds at 60 FPS)
FEVER_MODE_TRIGGER_INTERVAL = 400  # Start fever mode every 600 frames (10 seconds)

# Finale mode settings
FINALE_MODE_DURATION = 300  # frames (10 seconds at 60 FPS)
FINALE_HIT_COOLDOWN = 10  # Frames between freestyle hits (for rapid tapping)
FINALE_POINTS_PER_HIT = 50  # Points per freestyle hit in finale


class Note:
    def __init__(self, lane: str, y: float = 0, is_fever: bool = False):
        """
        Create a note that falls down the screen.
        
        Args:
            lane: 'Left' or 'Right'
            y: Starting Y position
            is_fever: Whether this note was spawned during fever mode
        """
        self.lane = lane
        self.y = y
        self.x = LEFT_LANE_X if lane == 'Left' else RIGHT_LANE_X
        self.width = NOTE_WIDTH
        self.height = NOTE_HEIGHT
        self.active = True
        self.hit = False
        self.is_fever = is_fever
        
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
        
        # Add purple glow for fever mode notes
        if self.is_fever:
            pygame.draw.rect(screen, PURPLE, rect, 4)
        
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


class LongNote(Note):
    """Long note that requires rapid hits to stack up points."""
    
    def __init__(self, lane: str, y: float = 0, is_fever: bool = False):
        """
        Create a long note that requires rapid hand movements.
        
        Args:
            lane: 'Left' or 'Right'
            y: Starting Y position
            is_fever: Whether this note was spawned during fever mode
        """
        super().__init__(lane, y, is_fever)
        self.height = LONG_NOTE_HEIGHT
        self.is_long_note = True
        self.hit_count = 0  # Track number of rapid hits
        self.hit_cooldown = 0  # Cooldown between hits
        self.in_hit_zone = False  # Track if note is currently in hit zone
        self.total_points = 0  # Total points earned from this note
        
    def update(self):
        """Move note downward and update cooldown."""
        # Move note downward
        self.y += NOTE_SPEED
        
        # Update hit cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        # Check if note is in hit zone (allow hitting throughout the long note)
        # More generous hit zone - check if ANY part of the long note overlaps with expanded hit zone
        note_top = self.y - self.height // 2
        note_bottom = self.y + self.height // 2
        hit_zone_top = HIT_ZONE_Y - OK_WINDOW - 20  # Extra buffer
        hit_zone_bottom = HIT_ZONE_Y + OK_WINDOW + 20  # Extra buffer
        
        # Note is in hit zone if there's any overlap
        self.in_hit_zone = not (note_bottom < hit_zone_top or note_top > hit_zone_bottom)
        
        # Deactivate if completely past the screen
        if self.y - self.height // 2 > SCREEN_HEIGHT + 50:
            self.active = False
    
    def can_hit(self) -> bool:
        """Check if the long note can be hit (in zone and cooldown expired)."""
        return self.in_hit_zone and self.hit_cooldown <= 0 and self.active
    
    def register_hit(self) -> int:
        """Register a rapid hit on this long note. Returns points earned."""
        if self.can_hit():
            self.hit_count += 1
            self.hit_cooldown = LONG_NOTE_HIT_COOLDOWN
            points = LONG_NOTE_POINTS_PER_HIT
            self.total_points += points
            return points
        return 0
    
    def draw(self, screen):
        """Draw the long note with special visual effects."""
        if not self.active:
            return
        
        # Base color
        color = BLUE if self.lane == 'Left' else RED
        
        # Make color brighter for long notes
        bright_color = tuple(min(255, c + 50) for c in color)
        
        # Draw long note rectangle
        rect = pygame.Rect(self.x - self.width // 2, int(self.y - self.height // 2), 
                          self.width, self.height)
        
        # Draw gradient effect for long notes
        for i in range(self.height):
            y_pos = int(self.y - self.height // 2 + i)
            alpha = 1 - (i / self.height) * 0.5
            gradient_color = tuple(int(c * alpha) for c in bright_color)
            pygame.draw.line(screen, gradient_color, 
                           (self.x - self.width // 2, y_pos),
                           (self.x + self.width // 2, y_pos))
        
        # Add visual feedback for hit readiness
        if self.in_hit_zone:
            if self.can_hit():
                # Green glow when ready to hit
                pygame.draw.rect(screen, GREEN, rect, 5)
            else:
                # Yellow glow when in cooldown
                pygame.draw.rect(screen, YELLOW, rect, 3)
        
        # Add purple glow for fever mode notes
        if self.is_fever:
            pygame.draw.rect(screen, PURPLE, rect, 4)
        
        # Draw border with special pattern
        pygame.draw.rect(screen, WHITE, rect, 2)
        
        # Draw stripes to indicate it's a long note
        for i in range(0, self.height, 20):
            stripe_y = int(self.y - self.height // 2 + i)
            pygame.draw.line(screen, YELLOW, 
                           (self.x - self.width // 2, stripe_y),
                           (self.x + self.width // 2, stripe_y), 2)
        
        # Draw hand indicator at center
        font = pygame.font.Font(None, 28)
        text = "👈 RAPID!" if self.lane == 'Left' else "RAPID! 👉"
        text_surface = font.render(text, True, YELLOW)
        text_rect = text_surface.get_rect(center=(self.x, int(self.y)))
        
        # Add black outline for text
        outline_font = pygame.font.Font(None, 28)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline_text = outline_font.render(text, True, BLACK)
            screen.blit(outline_text, (text_rect.x + dx, text_rect.y + dy))
        
        screen.blit(text_surface, text_rect)
        
        # Show hit count if any hits registered
        if self.hit_count > 0:
            count_text = font.render(f"x{self.hit_count}", True, GREEN)
            count_rect = count_text.get_rect(center=(self.x, int(self.y + 30)))
            screen.blit(count_text, count_rect)


class RhythmGame:
    def __init__(self, fullscreen: bool = False):
        self.fullscreen = fullscreen
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
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
        
        # Fever mode
        self.fever_mode = False
        self.fever_mode_timer = 0
        self.next_fever_mode_at = FEVER_MODE_TRIGGER_INTERVAL
        
        # Long note tracking
        self.long_note_hits = 0  # Total hits on long notes
        
        # Finale mode
        self.finale_mode = False
        self.finale_mode_timer = 0
        self.finale_hit_cooldown = 0
        self.finale_hits = 0  # Freestyle hits during finale
        self.finale_points = 0  # Points earned during finale
        
    def spawn_note(self):
        """Spawn a new note in random lane."""
        lane = random.choice(['Left', 'Right'])
        
        # Randomly spawn long notes
        if random.random() < LONG_NOTE_CHANCE:
            self.notes.append(LongNote(lane, is_fever=self.fever_mode))
        else:
            self.notes.append(Note(lane, is_fever=self.fever_mode))
        
        self.notes_spawned += 1
        
    def check_hit(self, hand: str) -> Optional[str]:
        """
        Check if a hand gesture hits a note.
        
        Args:
            hand: 'Left' or 'Right'
            
        Returns:
            Hit quality: 'perfect', 'good', 'ok', 'long_hit', or None
        """
        # Find closest active note in matching lane
        matching_notes = [n for n in self.notes if n.active and n.lane == hand]
        
        # Check for long notes first (they can be hit multiple times)
        long_notes = [n for n in matching_notes if isinstance(n, LongNote)]
        for long_note in long_notes:
            if long_note.can_hit():
                # Apply bonus multiplier during fever mode
                multiplier = 2 if self.fever_mode else 1
                points = long_note.register_hit() * multiplier
                self.score += points
                self.combo += 1
                self.long_note_hits += 1
                return 'long_hit'
        
        # For regular notes, find closest unhit note
        regular_notes = [n for n in matching_notes if not n.hit and not isinstance(n, LongNote)]
        
        if not regular_notes:
            return None
            
        # Get closest note to hit zone
        closest_note = min(regular_notes, key=lambda n: n.get_distance_from_hit_zone())
        distance = closest_note.get_distance_from_hit_zone()
        
        # Apply bonus multiplier during fever mode
        multiplier = 2 if self.fever_mode else 1
        
        # Check timing windows
        if distance <= PERFECT_WINDOW:
            closest_note.hit = True
            closest_note.active = False
            self.perfect_hits += 1
            self.score += 100 * multiplier
            self.combo += 1
            return 'perfect'
        elif distance <= GOOD_WINDOW:
            closest_note.hit = True
            closest_note.active = False
            self.good_hits += 1
            self.score += 50 * multiplier
            self.combo += 1
            return 'good'
        elif distance <= OK_WINDOW:
            closest_note.hit = True
            closest_note.active = False
            self.ok_hits += 1
            self.score += 25 * multiplier
            self.combo += 1
            return 'ok'
            
        return None
        
    def check_missed_notes(self):
        """Check for notes that passed the hit zone."""
        for note in self.notes:
            # Long notes handle their own deactivation
            if isinstance(note, LongNote):
                # Check if long note is finished and had no hits
                if not note.active and note.hit_count == 0 and not note.hit:
                    note.hit = True  # Mark as processed
                    self.misses += 1
                    self.combo = 0
                    self.show_feedback("MISS!", RED)
            else:
                # Regular notes
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
        
        # Finale mode: any hand movement scores points!
        if self.finale_mode:
            if self.finale_hit_cooldown <= 0:
                self.finale_hits += 1
                self.finale_points += FINALE_POINTS_PER_HIT
                self.score += FINALE_POINTS_PER_HIT
                self.combo += 1
                self.finale_hit_cooldown = FINALE_HIT_COOLDOWN
                self.show_feedback(f"FREESTYLE +{FINALE_POINTS_PER_HIT}!", GREEN)
                
                # Update max combo
                if self.combo > self.max_combo:
                    self.max_combo = self.combo
            
            self.last_hit_hand = hand
            return
            
        hit_quality = self.check_hit(hand)
        
        if hit_quality == 'perfect':
            feedback = "PERFECT! x2" if self.fever_mode else "PERFECT!"
            self.show_feedback(feedback, YELLOW)
            # Play 67 sound on perfect hit
            if self.sound_manager:
                self.sound_manager.play_count_sound()
        elif hit_quality == 'good':
            feedback = "GOOD! x2" if self.fever_mode else "GOOD!"
            self.show_feedback(feedback, GREEN)
        elif hit_quality == 'ok':
            feedback = "OK x2" if self.fever_mode else "OK"
            self.show_feedback(feedback, WHITE)
        elif hit_quality == 'long_hit':
            multiplier = "x2 " if self.fever_mode else ""
            feedback = f"RAPID {multiplier}+{LONG_NOTE_POINTS_PER_HIT * (2 if self.fever_mode else 1)}!"
            self.show_feedback(feedback, PURPLE)
        else:
            # Gesture but no note to hit (don't reset combo during finale)
            if not self.finale_mode:
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
        
        # Update finale hit cooldown
        if self.finale_hit_cooldown > 0:
            self.finale_hit_cooldown -= 1
        
        # Update finale mode
        if self.finale_mode:
            self.finale_mode_timer -= 1
            if self.finale_mode_timer <= 0:
                # Finale is over, end the game
                self.game_over = True
                if self.sound_manager:
                    self.sound_manager.stop_background_music()
                return
        
        # Check for fever mode trigger (don't trigger during finale)
        if self.frame_count >= self.next_fever_mode_at and not self.fever_mode and not self.finale_mode:
            self.fever_mode = True
            self.fever_mode_timer = FEVER_MODE_DURATION
            self.show_feedback("FEVER MODE!", PURPLE)
            
        # Update fever mode timer
        if self.fever_mode:
            self.fever_mode_timer -= 1
            if self.fever_mode_timer <= 0:
                self.fever_mode = False
                self.next_fever_mode_at = self.frame_count + FEVER_MODE_TRIGGER_INTERVAL
        
        # Spawn notes (faster during fever mode, not during finale)
        spawn_interval = FEVER_SPAWN_INTERVAL if self.fever_mode else SPAWN_INTERVAL
        if self.frame_count % spawn_interval == 0 and self.notes_spawned < self.max_notes and not self.finale_mode:
            self.spawn_note()
            
        # Update notes
        for note in self.notes:
            note.update()
            
        # Check for missed notes (not during finale)
        if not self.finale_mode:
            self.check_missed_notes()
        
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            
        # Check if all notes spawned and all have left the screen - trigger FINALE MODE!
        if self.notes_spawned >= self.max_notes and not self.finale_mode:
            active_notes = [n for n in self.notes if n.active]
            if len(active_notes) == 0:  # When all notes have left the screen, start finale
                self.finale_mode = True
                self.finale_mode_timer = FINALE_MODE_DURATION
                self.fever_mode = False  # End fever mode if active
                self.show_feedback("FINALE! GO CRAZY!", YELLOW)
                
    def draw(self):
        """Draw everything."""
        # Background
        self.screen.fill(BLACK)
        
        # Fever mode background effect
        if self.fever_mode and self.game_started and not self.game_over:
            # Pulsing background effect
            pulse = abs((self.fever_mode_timer % 30) - 15) / 15.0
            overlay_alpha = int(50 + pulse * 50)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(overlay_alpha)
            overlay.fill(PURPLE)
            self.screen.blit(overlay, (0, 0))
        
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
        
        # Draw fever mode banner on top of everything (drawn last so it's in front)
        if self.fever_mode and self.game_started and not self.game_over and not self.finale_mode:
            # Fever mode banner
            fever_text = self.big_font.render("FEVER MODE!", True, YELLOW)
            fever_rect = fever_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
            # Add outline for better visibility
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline_text = self.big_font.render("FEVER MODE!", True, BLACK)
                self.screen.blit(outline_text, (fever_rect.x + dx, fever_rect.y + dy))
            self.screen.blit(fever_text, fever_rect)
            
            # Show 2x multiplier
            multiplier_text = self.font.render("2x POINTS!", True, GREEN)
            mult_rect = multiplier_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
            self.screen.blit(multiplier_text, mult_rect)
        
        # Draw finale mode banner (takes over everything!)
        if self.finale_mode and self.game_started and not self.game_over:
            # Pulsing effect based on timer
            pulse = abs((self.finale_mode_timer % 20) - 10) / 10.0
            alpha = int(100 + pulse * 100)
            
            # Rainbow/multicolor background flash
            flash_colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (128, 0, 128)]
            flash_color = flash_colors[(self.finale_mode_timer // 10) % len(flash_colors)]
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(alpha)
            overlay.fill(flash_color)
            self.screen.blit(overlay, (0, 0))
            
            # FINALE banner
            finale_text = self.big_font.render("67 MODE!", True, YELLOW)
            finale_rect = finale_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            # Add outline
            for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
                outline_text = self.big_font.render("67 MODE!", True, BLACK)
                self.screen.blit(outline_text, (finale_rect.x + dx, finale_rect.y + dy))
            self.screen.blit(finale_text, finale_rect)
            
            # Instruction
            instruction_text = self.font.render("WAVE AS FAST AS YOU CAN!", True, WHITE)
            inst_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
            self.screen.blit(instruction_text, inst_rect)
            
            # Timer countdown
            timer_seconds = self.finale_mode_timer / 60.0
            timer_text = self.big_font.render(f"{timer_seconds:.1f}s", True, RED)
            timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
            # Add outline
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                outline_timer = self.big_font.render(f"{timer_seconds:.1f}s", True, BLACK)
                self.screen.blit(outline_timer, (timer_rect.x + dx, timer_rect.y + dy))
            self.screen.blit(timer_text, timer_rect)
            
            # Show finale stats
            stats_text = self.font.render(f"Freestyle Hits: {self.finale_hits}", True, GREEN)
            stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
            self.screen.blit(stats_text, stats_rect)
            
            points_text = self.font.render(f"Finale Points: {self.finale_points}", True, YELLOW)
            points_rect = points_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
            self.screen.blit(points_text, points_rect)
            
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
            f"Miss: {self.misses}",
            f"Rapid Hits: {self.long_note_hits}"
        ]
        for i, stat in enumerate(stats):
            color = PURPLE if "Rapid" in stat else GRAY
            stat_text = self.small_font.render(stat, True, color)
            self.screen.blit(stat_text, (10, stats_y))
            stats_y += 25
            
        # Progress
        progress = f"Notes: {self.notes_spawned}/{self.max_notes}"
        progress_text = self.small_font.render(progress, True, WHITE)
        self.screen.blit(progress_text, (SCREEN_WIDTH - 150, 10))
        
        # Fever mode timer
        if self.fever_mode:
            timer_seconds = self.fever_mode_timer / 60.0
            timer_text = self.small_font.render(f"Fever Time: {timer_seconds:.1f}s", True, PURPLE)
            self.screen.blit(timer_text, (SCREEN_WIDTH - 180, 40))
        
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
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        instructions = [
            "Wave hands to hit the notes!",
            "👈 LEFT hand for BLUE notes",
            "RIGHT hand 👉 for RED notes",
            "",
            "⚡ LONG NOTES: Rapid wave for bonus points!",
            "⚡ FEVER MODE: Get 2x points!",
            "🎉 FINALE: 10s freestyle at the end!",
            "",
            "Wave either hand to start!"
        ]
        
        y = 220
        for line in instructions:
            if not line:
                text = None
            elif "LONG NOTES" in line or "FEVER MODE" in line or "FINALE" in line:
                text = self.font.render(line, True, PURPLE)
            else:
                text = self.font.render(line, True, WHITE)
            
            if text:
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
            y += 30
            
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
            f"Long Note Hits: {self.long_note_hits}",
            f"Finale Hits: {self.finale_hits} (+{self.finale_points} pts)",
            "",
            "Press R to Restart",
            "Press ESC to Quit"
        ]
        
        y = 160
        for line in results:
            if not line:
                y += 15
                continue
                
            # Use smaller font for detailed stats
            if any(stat in line for stat in ["Perfect:", "Good:", "OK:", "Miss:", "Long Note Hits:"]):
                current_font = self.small_font
                step = 25
            else:
                current_font = self.font
                step = 35
                
            if "Finale Hits" in line:
                color = YELLOW
            else:
                color = WHITE
                
            text = current_font.render(line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += step
    
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
            target_width = 160
            target_height = 120
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
                            if self.sound_manager:
                                self.sound_manager.stop_background_music()
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
        if self.sound_manager:
            self.sound_manager.stop_background_music()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = RhythmGame()
    game.run()

