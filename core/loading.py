
import os
import pygame
import sys

class LoadingScreen:
    """Handles the loading screen animation."""
    
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.frames = []
        self._load_frames()
        
    def _load_frames(self):
        """Load loading animation frames."""
        try:
            # Navigate up from core/ to project root
            base_path = os.path.dirname(os.path.dirname(__file__))
            frames_dir = os.path.join(base_path, 'assets', 'loading_frames')
            
            if os.path.exists(frames_dir):
                # Get all jpg/png files and sort them
                files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.jpg') or f.endswith('.png')])
                for f in files:
                    try:
                        img = pygame.image.load(os.path.join(frames_dir, f)).convert()
                        self.frames.append(img)
                    except Exception as e:
                        print(f"Error loading frame {f}: {e}")
        except Exception as e:
            print(f"Error initializing loading frames: {e}")

    def play(self, duration_ms=3000):
        """Play the loading animation."""
        if not self.frames:
            return

        start_time = pygame.time.get_ticks()
        clock = pygame.time.Clock()
        
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - start_time
            
            if elapsed >= duration_ms:
                break
                
            # Calculate current frame
            if elapsed >= duration_ms:
                progress = 1.0
            else:
                progress = elapsed / duration_ms
                
            frame_idx = int(progress * len(self.frames))
            
            # Clamp index
            frame_idx = max(0, min(frame_idx, len(self.frames) - 1))
            
            # Draw frame
            # Clear screen (optional if frame covers everything)
            self.screen.fill((0, 0, 0))
            
            frame = self.frames[frame_idx]
            # Scale to current screen size
            curr_w, curr_h = self.screen.get_size()
            scaled_frame = pygame.transform.scale(frame, (curr_w, curr_h))
            
            self.screen.blit(scaled_frame, (0, 0))
            pygame.display.flip()
            
            # Handle events to keep window responsive and allow forced exit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Allow skipping loading? Or exiting?
                        # For now, let's treat ESC as skipping loading
                        return
            
            clock.tick(60)
