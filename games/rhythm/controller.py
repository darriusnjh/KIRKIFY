import pygame
import cv2
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from games.rhythm.game import RhythmGame
from core.hand_detector import HandDetector


class RhythmHandController:
    def __init__(self, use_hand_control: bool = True, model_type: str = "mediapipe", fullscreen: bool = False):
        """
        Initialize Rhythm Game controller with hand gesture detection.
        
        Args:
            use_hand_control: Whether to use hand gesture control
            model_type: Model type for hand detection ('mediapipe', 'prn', etc.)
            fullscreen: Whether to start in fullscreen mode
        """
        self.fullscreen = fullscreen
        self.game = RhythmGame(fullscreen=fullscreen)
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
                # Set camera resolution for wider field of view
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        else:
            self.hand_detector = None
            self.cap = None
        
        self.running = True
        self.last_hand_positions = {}  # Track positions per hand
        self.jump_threshold = 32  # pixels to move up to trigger gesture
        self.frame_skip = 1  # Process every frame for better responsiveness (reduced from 2)
        self.frame_counter = 0  # Frame counter for processing hand detection
        self.jump_cooldown = 0  # Cooldown counter for preventing rapid gestures
        self.jump_cooldown_frames = 3  # Cooldown period in frames (reduced from 10 for rapid notes)
        self.still_threshold = 1  # pixels - if hand moves less than this, consider it still
        self.reset_after_still_frames = 20  # Reset position after N frames of being still
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.game.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.game.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        # Note: All attributes are already initialized in __init__, no need to reset here
        
    def filter_hands(self, hands):
        """Filter hands to ensure only one left and one right hand maximum."""
        if len(hands) == 0:
            return hands
        
        valid_hands = [h for h in hands if h.get('handedness') in ['Left', 'Right']]
        
        if len(valid_hands) == 0:
            return []
        
        if len(valid_hands) == 1:
            return valid_hands
            
        left_hands = [h for h in valid_hands if h.get('handedness') == 'Left']
        right_hands = [h for h in valid_hands if h.get('handedness') == 'Right']
        
        if len(left_hands) == 1 and len(right_hands) == 1:
            return valid_hands
        
        if len(left_hands) >= 2 or len(right_hands) >= 2:
            sorted_hands = sorted(valid_hands, key=lambda h: h['confidence'], reverse=True)[:2]
            sorted_hands.sort(key=lambda h: h['center'][0])
            sorted_hands[0]['handedness'] = 'Left'
            sorted_hands[1]['handedness'] = 'Right'
            return sorted_hands
        
        if len(valid_hands) > 2:
            sorted_hands = sorted(valid_hands, key=lambda h: h['confidence'], reverse=True)[:2]
            sorted_hands.sort(key=lambda h: h['center'][0])
            sorted_hands[0]['handedness'] = 'Left'
            sorted_hands[1]['handedness'] = 'Right'
            return sorted_hands
        
        return valid_hands
        
    def process_hand_gesture(self, hands):
        """
        Process hand gesture to detect upward wave.
        Returns hand that performed gesture: 'Left', 'Right', or None
        """
        if not self.use_hand_control or self.hand_detector is None:
            return None
        
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        
        if len(hands) == 0:
            self.last_hand_positions.clear()
            return None
        
        gesture_hand = None
        
        if self.jump_cooldown <= 0:
            for hand in hands:
                center_y = hand['center'][1]
                handedness = hand.get('handedness', 'Unknown')
                
                if handedness == 'Unknown':
                    continue
                
                hand_key = handedness
                
                if hand_key in self.last_hand_positions:
                    hand_data = self.last_hand_positions[hand_key]
                    last_y = hand_data['y']
                    frames_still = hand_data.get('frames_still', 0)
                    
                    movement = abs(last_y - center_y)
                    
                    if frames_still >= self.reset_after_still_frames:
                        self.last_hand_positions[hand_key] = {
                            'y': center_y,
                            'frames_still': 0
                        }
                        continue
                    
                    if last_y - center_y > self.jump_threshold:
                        gesture_hand = handedness
                        self.jump_cooldown = self.jump_cooldown_frames
                        self.last_hand_positions[hand_key] = {
                            'y': center_y,
                            'frames_still': 0
                        }
                        break
                    
                    if movement < self.still_threshold:
                        self.last_hand_positions[hand_key] = {
                            'y': center_y,
                            'frames_still': frames_still + 1
                        }
                    else:
                        self.last_hand_positions[hand_key] = {
                            'y': center_y,
                            'frames_still': 0
                        }
                else:
                    self.last_hand_positions[hand_key] = {
                        'y': center_y,
                        'frames_still': 0
                    }
        else:
            for hand in hands:
                center_y = hand['center'][1]
                handedness = hand.get('handedness', 'Unknown')
                if handedness != 'Unknown':
                    hand_key = handedness
                    
                    if hand_key in self.last_hand_positions:
                        hand_data = self.last_hand_positions[hand_key]
                        last_y = hand_data['y']
                        frames_still = hand_data.get('frames_still', 0)
                        movement = abs(last_y - center_y)
                        
                        if movement < self.still_threshold:
                            self.last_hand_positions[hand_key] = {
                                'y': center_y,
                                'frames_still': frames_still + 1
                            }
                        else:
                            self.last_hand_positions[hand_key] = {
                                'y': center_y,
                                'frames_still': 0
                            }
                    else:
                        self.last_hand_positions[hand_key] = {
                            'y': center_y,
                            'frames_still': 0
                        }
        
        detected_keys = set(hand.get('handedness') for hand in hands if hand.get('handedness') != 'Unknown')
        keys_to_remove = [k for k in self.last_hand_positions.keys() if k not in detected_keys]
        for key in keys_to_remove:
            del self.last_hand_positions[key]
        
        return gesture_hand
    
    def run(self):
        """
        Main game loop with hand gesture control.
        
        Returns:
            'main_menu' if user wants to return to main menu, 'exit' if user wants to exit, None otherwise
        """
        # Show loading screen
        try:
            from core.loading import LoadingScreen
            loading = LoadingScreen(self.game.screen)
            loading.play()
        except Exception as e:
            print(f"Error showing loading screen: {e}")

        while self.running:
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'exit'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        # Toggle fullscreen
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        # Show pause menu
                        try:
                            from ui.pause_menu import PauseMenu
                            
                            # Get screen dimensions
                            screen_width = self.game.screen.get_width()
                            screen_height = self.game.screen.get_height()
                            
                            pause_menu = PauseMenu(
                                self.game.screen,
                                screen_width,
                                screen_height
                            )
                            # Capture current screen as background
                            background = self.game.screen.copy()
                            result = pause_menu.run(background)
                            
                            if result == 'main_menu':
                                self.running = False
                                return 'main_menu'
                            elif result == 'exit':
                                self.running = False
                                return 'exit'
                            # If 'resume', continue game loop
                        except Exception as e:
                            print(f"Error showing pause menu: {e}")
                            import traceback
                            traceback.print_exc()
                    elif event.key == pygame.K_r and self.game.game_over:
                        self.game.reset()
                    # Keyboard controls for testing
                    elif event.key == pygame.K_a:
                        self.game.handle_hand_gesture('Left')
                    elif event.key == pygame.K_l:
                        self.game.handle_hand_gesture('Right')
            
            # Process hand gesture control
            if self.use_hand_control and self.cap is not None:
                self.frame_counter += 1
                if self.frame_counter % self.frame_skip == 0:
                    ret, frame = self.cap.read()
                    if ret:
                        frame = cv2.flip(frame, 1)
                        hands_raw = self.hand_detector.detect_hands(frame)
                        hands = self.filter_hands(hands_raw)
                        
                        self.detected_hands_info = hands
                        
                        # Draw hand detection boxes on frame
                        frame_with_boxes = self.hand_detector.draw_detections(frame, hands)
                        
                        # Convert to Pygame surface for display
                        frame_rgb = cv2.cvtColor(frame_with_boxes, cv2.COLOR_BGR2RGB)
                        frame_surface = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.shape[1::-1], "RGB")
                        
                        # Set webcam surface and hand info on game
                        self.game.set_webcam_surface(frame_surface)
                        self.game.set_detected_hands(hands)
                        
                        # Process gesture
                        gesture_hand = self.process_hand_gesture(hands)
                        if gesture_hand:
                            self.game.handle_hand_gesture(gesture_hand)
            
            # Update and draw game (game.draw() includes webcam overlay now)
            self.game.update()
            self.game.draw()
            
            self.game.clock.tick(60)
        
        # Cleanup
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        # Note: Don't quit pygame here - menu may still be running
        return None  # Game ended normally


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rhythm Game with Hand Gesture Control')
    parser.add_argument('--no-hand', action='store_true',
                       help='Disable hand gesture control (use keyboard only)')
    parser.add_argument('-m', '--model', type=str, default='mediapipe',
                       choices=['mediapipe', 'prn', 'tiny', 'v4-tiny', 'yolo'],
                       help='Hand detection model to use (default: mediapipe)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Rhythm Hand Game")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Hand Control: {'Enabled' if not args.no_hand else 'Disabled'}")
    print("\nControls:")
    print("  - 👈 Wave LEFT hand for BLUE notes")
    print("  - Wave RIGHT hand 👉 for RED notes")
    print("  - Hit notes at the YELLOW line for points!")
    if args.model == 'mediapipe':
        print("  - MediaPipe detects left/right hands automatically!")
    print("  - Keyboard: A = Left, L = Right (for testing)")
    print("  - Press R to restart after game over")
    print("  - Press ESC to quit")
    print("=" * 60)
    print()
    
    controller = RhythmHandController(
        use_hand_control=not args.no_hand,
        model_type=args.model
    )
    controller.run()


if __name__ == "__main__":
    main()

