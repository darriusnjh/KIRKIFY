import pygame
import random
import json
import os
import sys
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.7
JUMP_STRENGTH = -6  # Reduced from -8 to -4 (half the jump height)
PIPE_WIDTH = 60
PIPE_GAP = 150
PIPE_SPEED = 3
PIPE_SPAWN_RATE = 90  # frames between pipe spawns
GROUND_HEIGHT = 100

# Colors (Flappy Bird style)
SKY_BLUE = (135, 206, 250)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)


class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.radius = 15
        self.rotation = 0
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Rotation based on velocity
        self.rotation = min(max(self.velocity * 3, -30), 90)
        
    def jump(self):
        self.velocity = JUMP_STRENGTH
        
    def draw(self, screen):
        # Draw bird as a circle with a small triangle for beak
        center = (int(self.x), int(self.y))
        pygame.draw.circle(screen, YELLOW, center, self.radius)
        pygame.draw.circle(screen, BLACK, center, self.radius, 2)
        
        # Draw eye
        eye_pos = (int(self.x + 5), int(self.y - 5))
        pygame.draw.circle(screen, BLACK, eye_pos, 3)
        
        # Draw beak
        beak_points = [
            (int(self.x + self.radius), int(self.y)),
            (int(self.x + self.radius + 8), int(self.y - 3)),
            (int(self.x + self.radius + 8), int(self.y + 3))
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(150, SCREEN_HEIGHT - GROUND_HEIGHT - 150)
        self.passed = False
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def draw(self, screen):
        # Top pipe
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP // 2)
        pygame.draw.rect(screen, GREEN, top_rect)
        pygame.draw.rect(screen, BLACK, top_rect, 3)
        
        # Bottom pipe
        bottom_y = self.gap_y + PIPE_GAP // 2
        bottom_rect = pygame.Rect(self.x, bottom_y, PIPE_WIDTH, 
                                  SCREEN_HEIGHT - GROUND_HEIGHT - bottom_y)
        pygame.draw.rect(screen, GREEN, bottom_rect)
        pygame.draw.rect(screen, BLACK, bottom_rect, 3)
        
        # Pipe caps
        cap_width = PIPE_WIDTH + 10
        top_cap = pygame.Rect(self.x - 5, self.gap_y - PIPE_GAP // 2 - 20, 
                             cap_width, 20)
        bottom_cap = pygame.Rect(self.x - 5, self.gap_y + PIPE_GAP // 2, 
                                 cap_width, 20)
        pygame.draw.rect(screen, GREEN, top_cap)
        pygame.draw.rect(screen, BLACK, top_cap, 3)
        pygame.draw.rect(screen, GREEN, bottom_cap)
        pygame.draw.rect(screen, BLACK, bottom_cap, 3)
        
    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP // 2)
        bottom_y = self.gap_y + PIPE_GAP // 2
        bottom_rect = pygame.Rect(self.x, bottom_y, PIPE_WIDTH, 
                                  SCREEN_HEIGHT - GROUND_HEIGHT - bottom_y)
        return [top_rect, bottom_rect]
    
    def check_collision(self, bird_rect):
        for rect in self.get_rects():
            if bird_rect.colliderect(rect):
                return True
        return False


class Game:
    def __init__(self, sound_manager=None):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.sound_manager = sound_manager
        self.reset()
        self.high_score = self.load_high_score()
        
    def reset(self):
        self.bird = Bird(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.frame_count = 0
        self.webcam_surface = None
        self.detected_hands_info = None  # Store hand detection info for display
        self.next_jump_hand = 'Either'  # Which hand should jump next (for alternating)
        self.hands_corrected = False  # Whether hands were auto-corrected
        
    def load_high_score(self):
        try:
            if os.path.exists('high_scores.json'):
                with open('high_scores.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            with open('high_scores.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def set_webcam_frame(self, surface):
        self.webcam_surface = surface
    
    def set_detected_hands(self, hands_info, next_hand=None, corrected=False):
        """Store information about detected hands for display."""
        self.detected_hands_info = hands_info
        self.next_jump_hand = next_hand  # Which hand should jump next
        self.hands_corrected = corrected  # Whether hands were reassigned
    
    def handle_jump(self):
        if not self.game_over:
            if not self.game_started:
                self.game_started = True
            self.bird.jump()
            return True
        return False
    
    def update(self):
        if not self.game_started or self.game_over:
            return
            
        self.frame_count += 1
        self.bird.update()
        
        # Spawn pipes
        if self.frame_count % PIPE_SPAWN_RATE == 0:
            self.pipes.append(Pipe(SCREEN_WIDTH))
        
        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            
            # Check if bird passed pipe
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1
                if self.sound_manager:
                    self.sound_manager.play_score_sound()
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
            
            # Remove off-screen pipes
            if pipe.x + PIPE_WIDTH < 0:
                self.pipes.remove(pipe)
        
        # Check collisions
        bird_rect = self.bird.get_rect()
        
        # Ground and ceiling collision
        if (self.bird.y + self.bird.radius >= SCREEN_HEIGHT - GROUND_HEIGHT or 
            self.bird.y - self.bird.radius <= 0):
            if self.sound_manager:
                self.sound_manager.play_hit_sound()
            self.game_over = True
            return
        
        # Pipe collision
        for pipe in self.pipes:
            if pipe.check_collision(bird_rect):
                if self.sound_manager:
                    self.sound_manager.play_hit_sound()
                self.game_over = True
                return
    
    def draw(self):
        # Draw sky background
        self.screen.fill(SKY_BLUE)
        
        # Draw clouds (simple circles)
        for i in range(3):
            x = (i * 150 + self.frame_count // 2) % (SCREEN_WIDTH + 100) - 50
            y = 50 + i * 80
            pygame.draw.circle(self.screen, WHITE, (x, y), 30)
            pygame.draw.circle(self.screen, WHITE, (x + 20, y), 35)
            pygame.draw.circle(self.screen, WHITE, (x + 40, y), 30)
        
        if self.game_started:
            # Draw pipes
            for pipe in self.pipes:
                pipe.draw(self.screen)
            
            # Draw bird
            self.bird.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(str(self.score), True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            # Add shadow
            shadow_text = self.font.render(str(self.score), True, BLACK)
            shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 2, 52))
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(score_text, score_rect)
        else:
            # Draw start screen
            start_text = self.big_font.render("FLAPPY BIRD", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            shadow_text = self.big_font.render("FLAPPY BIRD", True, BLACK)
            shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 - 47))
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(start_text, start_rect)
            
            instruction_text = self.font.render("Alternate L/R Hands to Jump!", True, BLACK)
            inst_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(instruction_text, inst_rect)
            
            instruction_text2 = pygame.font.Font(None, 24).render("Wave Left, then Right, then Left...", True, BLACK)
            inst_rect2 = instruction_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            self.screen.blit(instruction_text2, inst_rect2)
            
            # Draw bird at start position
            self.bird.draw(self.screen)
        
        # Draw ground
        ground_rect = pygame.Rect(0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT)
        pygame.draw.rect(self.screen, BROWN, ground_rect)
        pygame.draw.line(self.screen, BLACK, (0, SCREEN_HEIGHT - GROUND_HEIGHT), 
                        (SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT), 3)
        
        # Draw grass on ground
        for i in range(0, SCREEN_WIDTH, 20):
            pygame.draw.line(self.screen, GREEN, 
                           (i, SCREEN_HEIGHT - GROUND_HEIGHT),
                           (i + 10, SCREEN_HEIGHT - GROUND_HEIGHT - 10), 2)
        
        if self.game_over:
            # Draw game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("GAME OVER", True, WHITE)
            go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(game_over_text, go_rect)
            
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(score_text, score_rect)
            
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
            hs_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(high_score_text, hs_rect)
            
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, restart_rect)
        
        # Draw webcam feed if available
        if self.webcam_surface:
            # Scale to reasonable size (e.g., 25% of width)
            w = 120
            h = 90
            scaled_surface = pygame.transform.scale(self.webcam_surface, (w, h))
            # Position in bottom-right corner
            self.screen.blit(scaled_surface, (SCREEN_WIDTH - w - 10, SCREEN_HEIGHT - h - 10))
            # Draw border
            pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH - w - 10, SCREEN_HEIGHT - h - 10, w, h), 2)
        
        # Draw hand detection status
        if self.detected_hands_info is not None:
            hand_info_font = pygame.font.Font(None, 24)
            next_hand_font = pygame.font.Font(None, 32)
            y_offset = 10
            
            # Show which hand should jump next (BIG and BOLD)
            if hasattr(self, 'next_jump_hand') and self.next_jump_hand:
                if self.next_jump_hand == 'Either':
                    next_text = "Wave Either Hand!"
                    next_color = (255, 255, 100)  # Yellow
                elif self.next_jump_hand == 'Left':
                    next_text = "Wave LEFT Hand! 👈"
                    next_color = (100, 150, 255)  # Blue
                else:  # Right
                    next_text = "Wave RIGHT Hand! 👉"
                    next_color = (255, 100, 100)  # Red
                
                next_hand_text = next_hand_font.render(next_text, True, next_color)
                # Add thick black outline for emphasis
                outline_text = next_hand_font.render(next_text, True, BLACK)
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            self.screen.blit(outline_text, (10 + dx, y_offset + dy))
                self.screen.blit(next_hand_text, (10, y_offset))
                y_offset += 40
            
            # Count detected left and right hands
            left_count = sum(1 for h in self.detected_hands_info if h.get('handedness') == 'Left')
            right_count = sum(1 for h in self.detected_hands_info if h.get('handedness') == 'Right')
            
            # Show correction status if hands were reassigned
            if hasattr(self, 'hands_corrected') and self.hands_corrected:
                hands_status = f"Hands: L={left_count} R={right_count} [Auto-corrected by position]"
                status_color = (255, 200, 100)  # Orange for corrected
            else:
                hands_status = f"Hands: L={left_count} R={right_count}"
                status_color = (180, 180, 180)  # Gray for normal
            
            status_text = hand_info_font.render(hands_status, True, status_color)
            outline_text = hand_info_font.render(hands_status, True, BLACK)
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                self.screen.blit(outline_text, (10 + dx, y_offset + dy))
            self.screen.blit(status_text, (10, y_offset))
            y_offset += 25
            
            if len(self.detected_hands_info) > 0:
                for hand in self.detected_hands_info:
                    handedness = hand.get('handedness', 'Hand')
                    confidence = hand.get('confidence', 0)
                    
                    # Check if this is a dummy hand (0% confidence)
                    is_dummy = confidence == 0.0
                    
                    # Choose color based on handedness
                    if handedness == 'Left':
                        color = (100, 100, 255) if not is_dummy else (80, 80, 180)  # Light blue for left, darker if dummy
                    elif handedness == 'Right':
                        color = (255, 100, 100) if not is_dummy else (180, 80, 80)  # Light red for right, darker if dummy
                    else:
                        color = (100, 255, 100)  # Light green for unknown
                    
                    # Highlight the hand that should jump next
                    if hasattr(self, 'next_jump_hand') and handedness == self.next_jump_hand:
                        color = (255, 255, 0)  # Bright yellow for active hand
                        text = f">>> {handedness} Hand: {confidence:.0%}" + (" [No Detection]" if is_dummy else "") + " <<<"
                    else:
                        text = f"{handedness} Hand: {confidence:.0%}" + (" [No Detection]" if is_dummy else "")
                    
                    hand_text = hand_info_font.render(text, True, color)
                    # Add black outline for better visibility
                    outline_text = hand_info_font.render(text, True, BLACK)
                    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                        self.screen.blit(outline_text, (10 + dx, y_offset + dy))
                    self.screen.blit(hand_text, (10, y_offset))
                    y_offset += 25
            else:
                # No hands detected
                text = "No hands detected"
                no_hand_text = hand_info_font.render(text, True, (200, 200, 200))
                outline_text = hand_info_font.render(text, True, BLACK)
                for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    self.screen.blit(outline_text, (10 + dx, 10 + dy))
                self.screen.blit(no_hand_text, (10, 10))
        
        pygame.display.flip()
    
    def restart(self):
        self.reset()
