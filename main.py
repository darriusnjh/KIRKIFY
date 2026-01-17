import pygame
import cv2
import numpy as np
import sys
from game import Game
from hand_detector import HandDetector
from sound_manager import SoundManager


class FlappyBirdController:
    def __init__(self, use_hand_control: bool = True, model_type: str = "tiny"):
        """
        Initialize Flappy Bird game controller.
        
        Args:
            use_hand_control: Whether to use hand gesture control
            model_type: YOLO model type for hand detection
        """
        self.sound_manager = SoundManager()
        self.game = Game(sound_manager=self.sound_manager)
        self.use_hand_control = use_hand_control
        
        if use_hand_control:
            self.hand_detector = HandDetector(model_type=model_type)
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Warning: Could not open webcam. Falling back to keyboard control.")
                self.use_hand_control = False
                self.cap = None
        else:
            self.hand_detector = None
            self.cap = None
        
        self.running = True
        self.last_hand_y = None
        self.jump_threshold = 30  # pixels to move up to trigger jump
        self.frame_skip = 2  # Process every Nth frame for performance
        self.frame_counter = 0
        
    def process_hand_gesture(self, hands):
        """Process hand gesture to detect jump command."""
        if not self.use_hand_control or self.hand_detector is None:
            return False
        
        # hands argument is now passed in, no need to detect again
        
        if len(hands) > 0:
            # Get the hand with highest confidence
            hand = max(hands, key=lambda h: h['confidence'])
            center_y = hand['center'][1]
            
            # Detect upward movement
            if self.last_hand_y is not None:
                if self.last_hand_y - center_y > self.jump_threshold:
                    self.last_hand_y = center_y
                    return True
            
            self.last_hand_y = center_y
        
        return False
    
    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game.handle_jump():
                            self.sound_manager.play_jump_sound()
                    elif event.key == pygame.K_r and self.game.game_over:
                        self.game.restart()
                        self.sound_manager.play_start_sound()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Process hand gesture control
            if self.use_hand_control and self.cap is not None:
                self.frame_counter += 1
                if self.frame_counter % self.frame_skip == 0:
                    ret, frame = self.cap.read()
                    if ret:
                        # Flip frame horizontally for mirror effect
                        frame = cv2.flip(frame, 1)
                        # Detect hands first
                        hands = self.hand_detector.detect_hands(frame)
                        
                        # Draw detections on frame
                        frame_with_boxes = self.hand_detector.draw_detections(frame, hands)
                        
                        # Convert to Pygame surface and update game
                        frame_rgb = cv2.cvtColor(frame_with_boxes, cv2.COLOR_BGR2RGB)
                        frame_surface = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.shape[1::-1], "RGB")
                        self.game.set_webcam_frame(frame_surface)
                        
                        # Process gesture using already detected hands
                        if self.process_hand_gesture(hands):
                            if self.game.handle_jump():
                                self.sound_manager.play_jump_sound()
            
            # Update game
            self.game.update()
            
            # Draw game
            self.game.draw()
            
            # Start background music when game starts
            if self.game.game_started and not self.sound_manager.music_playing:
                self.sound_manager.start_background_music()
            
            # Play background music
            self.sound_manager.update()
            
            clock.tick(60)
        
        # Cleanup
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        pygame.quit()
        sys.exit()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Flappy Bird with Hand Gesture Control')
    parser.add_argument('--no-hand', action='store_true', 
                       help='Disable hand gesture control (use keyboard only)')
    parser.add_argument('-n', '--network', type=str, default='tiny',
                       choices=['tiny', 'prn', 'v4-tiny', 'yolo'],
                       help='YOLO model type to use (default: tiny)')
    
    args = parser.parse_args()
    
    controller = FlappyBirdController(
        use_hand_control=not args.no_hand,
        model_type=args.network
    )
    controller.run()


if __name__ == "__main__":
    main()
