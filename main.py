import pygame
import cv2
import sys
from game import Game
from hand_detector import HandDetector
from sound_manager import SoundManager


class FlappyBirdController:
    def __init__(self, use_hand_control: bool = True, model_type: str = "tiny", 
                 debug_visualization: bool = False):
        """
        Initialize Flappy Bird game controller.
        
        Args:
            use_hand_control: Whether to use hand gesture control
            model_type: YOLO model type for hand detection
            debug_visualization: Show hand detection window for debugging
        """
        self.sound_manager = SoundManager()
        self.game = Game(sound_manager=self.sound_manager)
        self.use_hand_control = use_hand_control
        self.debug_visualization = debug_visualization
        
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
        self.movement_threshold = 30  # pixels of movement to detect gesture
        self.frame_skip = 2  # Process every Nth frame for performance
        self.frame_counter = 0
        
    def process_hand_gesture(self, frame):
        """
        Process dual-hand gesture to detect jump command.
        Requires both hands: one goes up while the other goes down.
        """
        if not self.use_hand_control or self.hand_detector is None:
            return False
        
        # Use the new dual-hand gesture detection
        return self.hand_detector.detect_dual_hand_gesture(frame, self.movement_threshold)
    
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
                        
                        # Process gesture
                        if self.process_hand_gesture(frame):
                            if self.game.handle_jump():
                                self.sound_manager.play_jump_sound()
                        
                        # Draw detections (if debug visualization is enabled)
                        if self.debug_visualization:
                            hands = self.hand_detector.detect_hands(frame)
                            frame_width = frame.shape[1]
                            identified = self.hand_detector.identify_hands(hands, frame_width)
                            frame = self.hand_detector.draw_detections(frame, hands, identified)
                            
                            # Add instruction text
                            cv2.putText(frame, "Both hands required: Left up + Right down = Jump", 
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            
                            cv2.imshow('Hand Detection - Both Hands Required', frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                self.running = False
            
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
    parser.add_argument('--debug', action='store_true',
                       help='Show hand detection visualization window')
    
    args = parser.parse_args()
    
    controller = FlappyBirdController(
        use_hand_control=not args.no_hand,
        model_type=args.network,
        debug_visualization=args.debug
    )
    controller.run()


if __name__ == "__main__":
    main()
