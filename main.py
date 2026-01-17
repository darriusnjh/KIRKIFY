import pygame
import cv2
import numpy as np
import sys
from game import Game
from hand_detector import HandDetector
from sound_manager import SoundManager


class FlappyBirdController:
    def __init__(self, use_hand_control: bool = True, model_type: str = "mediapipe"):
        """
        Initialize Flappy Bird game controller.
        
        Args:
            use_hand_control: Whether to use hand gesture control
            model_type: Model type for hand detection ('mediapipe', 'tiny', 'prn', etc.)
        """
        self.sound_manager = SoundManager()
        self.game = Game(sound_manager=self.sound_manager)
        self.use_hand_control = use_hand_control
        
        if use_hand_control:
            print(f"Initializing hand detector with {model_type} model...")
            self.hand_detector = HandDetector(model_type=model_type)
            
            # Check if detector loaded successfully
            if model_type == "mediapipe":
                if self.hand_detector.hands_detector is None:
                    print("Warning: MediaPipe failed to load. Trying YOLO fallback...")
                    if self.hand_detector.net is None:
                        print("Warning: No working hand detection model. Falling back to keyboard control.")
                        self.use_hand_control = False
                        self.hand_detector = None
                        self.cap = None
                        return
            elif self.hand_detector.net is None:
                print("Warning: Hand detection model failed to load. Falling back to keyboard control.")
                self.use_hand_control = False
                self.hand_detector = None
                self.cap = None
                return
            
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Warning: Could not open webcam. Falling back to keyboard control.")
                self.use_hand_control = False
                self.cap = None
                self.hand_detector = None
        else:
            self.hand_detector = None
            self.cap = None
        
        self.running = True
        self.last_hand_positions = {}  # Track positions per hand
        self.jump_threshold = 30  # pixels to move up to trigger jump
        self.frame_skip = 2  # Process every Nth frame for performance
        self.frame_counter = 0
        
    def process_hand_gesture(self, hands):
        """
        Process hand gesture to detect jump command.
        Supports both single hand (any hand) and left/right hand specific detection.
        """
        if not self.use_hand_control or self.hand_detector is None:
            return False
        
        if len(hands) == 0:
            # Clear tracked positions if no hands detected
            self.last_hand_positions.clear()
            return False
        
        should_jump = False
        
        # Process each detected hand
        for hand in hands:
            center_y = hand['center'][1]
            handedness = hand.get('handedness', 'Unknown')  # 'Left', 'Right', or 'Unknown'
            
            # Use handedness as key if available, otherwise use generic key
            hand_key = handedness if handedness != 'Unknown' else 'hand'
            
            # Detect upward movement for this specific hand
            if hand_key in self.last_hand_positions:
                last_y = self.last_hand_positions[hand_key]
                
                # Check if hand moved up significantly (jump gesture)
                if last_y - center_y > self.jump_threshold:
                    should_jump = True
                    # Update position after detecting jump to avoid multiple jumps
                    self.last_hand_positions[hand_key] = center_y
            else:
                # First time seeing this hand, just track it
                self.last_hand_positions[hand_key] = center_y
            
            # Always update position
            self.last_hand_positions[hand_key] = center_y
        
        # Clean up old hand positions (hands that are no longer detected)
        detected_keys = set(hand.get('handedness', 'hand') for hand in hands)
        keys_to_remove = [k for k in self.last_hand_positions.keys() if k not in detected_keys and k != 'hand']
        for key in keys_to_remove:
            del self.last_hand_positions[key]
        
        return should_jump
    
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
                        
                        # Update game with detected hands info
                        self.game.set_detected_hands(hands)
                        
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
    parser.add_argument('-m', '--model', type=str, default='mediapipe',
                       choices=['mediapipe', 'tiny', 'prn', 'v4-tiny', 'yolo'],
                       help='Hand detection model to use (default: mediapipe)')
    # Keep -n for backward compatibility
    parser.add_argument('-n', '--network', type=str,
                       choices=['tiny', 'prn', 'v4-tiny', 'yolo'],
                       help='(Deprecated: use -m) YOLO model type to use')
    
    args = parser.parse_args()
    
    # Use network argument if provided (backward compatibility), otherwise use model
    model_type = args.network if args.network else args.model
    
    print("=" * 60)
    print("Flappy Bird with Hand Gesture Control")
    print("=" * 60)
    print(f"Model: {model_type}")
    print(f"Hand Control: {'Enabled' if not args.no_hand else 'Disabled'}")
    print("\nControls:")
    print("  - Wave hand UP to make the bird jump")
    if model_type == 'mediapipe':
        print("  - Works with left hand, right hand, or both!")
    print("  - Press SPACE for keyboard jump")
    print("  - Press R to restart after game over")
    print("  - Press ESC to quit")
    print("=" * 60)
    print()
    
    controller = FlappyBirdController(
        use_hand_control=not args.no_hand,
        model_type=model_type
    )
    controller.run()


if __name__ == "__main__":
    main()
