import pygame
import cv2
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from games.flappy_bird.game import Game
from core.hand_detector import HandDetector
from core.sound_manager import SoundManager


class FlappyBirdController:
    def __init__(self, use_hand_control: bool = True, model_type: str = "mediapipe", fullscreen: bool = False):
        """
        Initialize Flappy Bird game controller.
        
        Args:
            use_hand_control: Whether to use hand gesture control
            model_type: Model type for hand detection ('mediapipe', 'tiny', 'prn', etc.)
            fullscreen: Whether to start in fullscreen mode
        """
        self.fullscreen = fullscreen
        self.sound_manager = SoundManager()
        self.game = Game(sound_manager=self.sound_manager, fullscreen=fullscreen)
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
                # Set camera resolution for wider field of view (if supported)
                # Higher resolution = more area captured = "zoomed out" effect
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Try 1280x720 (720p)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                # Note: Not all cameras support all resolutions, it will fallback to closest supported
        else:
            self.hand_detector = None
            self.cap = None
        
        self.running = True
        self.last_hand_positions = {}  # Track positions per hand: {hand_key: {'y': y_pos, 'frames_still': count}}
        self.last_jump_hand = None  # Track which hand performed the last jump (for alternating)
        self.jump_threshold = 32  # pixels to move up to trigger jump (increased by 2 for less sensitivity)
        self.frame_skip = 1  # Process every frame for better responsiveness (reduced from 2)
        self.frame_counter = 0
        self.jump_cooldown = 1  # Frames until next jump allowed
        self.jump_cooldown_frames = 0  # Cooldown period (5 frames = ~0.08s at 60 FPS)
        self.still_threshold = 10  # pixels - if hand moves less than this, consider it still
        self.reset_after_still_frames = 20  # Reset position after 30 frames (~0.5s) of being still
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.game.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            from games.flappy_bird.game import SCREEN_WIDTH, SCREEN_HEIGHT
            self.game.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        # Note: All attributes are already initialized in __init__, no need to reset here
        
    def filter_hands(self, hands):
        """
        Filter and correct hands to ensure only one left and one right hand maximum.
        If 2 hands of same type detected, reassign them as left/right based on position.
        
        Args:
            hands: List of detected hands
            
        Returns:
            Filtered list with max 2 hands (one left, one right)
        """
        if len(hands) == 0:
            return hands
        
        # Only keep hands with valid handedness
        valid_hands = [h for h in hands if h.get('handedness') in ['Left', 'Right']]
        
        if len(valid_hands) == 0:
            return []
        
        if len(valid_hands) == 1:
            return valid_hands
            
        # Count left and right hands
        left_hands = [h for h in valid_hands if h.get('handedness') == 'Left']
        right_hands = [h for h in valid_hands if h.get('handedness') == 'Right']
        
        # If we have proper distribution (1 left, 1 right), return as is
        if len(left_hands) == 1 and len(right_hands) == 1:
            return valid_hands
        
        # If we have 2+ of the same hand type, enforce left/right by position
        if len(left_hands) >= 2 or len(right_hands) >= 2:
            print(f"[Filter] Detected {len(left_hands)} left, {len(right_hands)} right - enforcing L/R by position")
            
            # Take the 2 hands with highest confidence
            sorted_hands = sorted(valid_hands, key=lambda h: h['confidence'], reverse=True)[:2]
            
            # Sort by X position (leftmost to rightmost)
            sorted_hands.sort(key=lambda h: h['center'][0])
            
            # Assign: leftmost = Left hand, rightmost = Right hand
            sorted_hands[0]['handedness'] = 'Left'
            sorted_hands[1]['handedness'] = 'Right'
            
            print(f"[Filter] Reassigned hands as Left (x={sorted_hands[0]['center'][0]}) and Right (x={sorted_hands[1]['center'][0]})")
            
            return sorted_hands
        
        # If we have more than 2 hands total, take best 2 by confidence
        if len(valid_hands) > 2:
            print(f"[Filter] More than 2 hands detected ({len(valid_hands)}), keeping best 2 by confidence")
            sorted_hands = sorted(valid_hands, key=lambda h: h['confidence'], reverse=True)[:2]
            
            # Sort by X position and assign left/right
            sorted_hands.sort(key=lambda h: h['center'][0])
            sorted_hands[0]['handedness'] = 'Left'
            sorted_hands[1]['handedness'] = 'Right'
            
            return sorted_hands
        
        # Default: return the valid hands we have
        return valid_hands
    
    def process_hand_gesture(self, hands):
        """
        Process hand gesture to detect jump command.
        REQUIRES ALTERNATING between left and right hands!
        Wave left hand, then right hand, then left again, etc.
        
        Improved: Resets position tracking after hand is still to prevent stale tracking.
        """
        if not self.use_hand_control or self.hand_detector is None:
            return False
        
        # Decrement cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        
        if len(hands) == 0:
            # Clear tracked positions if no hands detected
            self.last_hand_positions.clear()
            return False
        
        should_jump = False
        jump_hand = None
        
        # Only check for jumps if cooldown expired
        if self.jump_cooldown <= 0:
            # Process each detected hand
            for hand in hands:
                center_y = hand['center'][1]
                handedness = hand.get('handedness', 'Unknown')  # 'Left', 'Right', or 'Unknown'
                
                # Skip hands without proper handedness detection (need L/R for alternating)
                if handedness == 'Unknown':
                    continue
                
                hand_key = handedness
                
                # Check if we have previous position data for this hand
                if hand_key in self.last_hand_positions:
                    hand_data = self.last_hand_positions[hand_key]
                    last_y = hand_data['y']
                    frames_still = hand_data.get('frames_still', 0)
                    
                    # Calculate movement
                    movement = abs(last_y - center_y)
                    
                    # Check if hand has been still too long - reset tracking if so
                    if frames_still >= self.reset_after_still_frames:
                        # Reset this hand's position - treat as first detection
                        self.last_hand_positions[hand_key] = {
                            'y': center_y,
                            'frames_still': 0
                        }
                        continue
                    
                    # Check if hand moved up significantly (jump gesture)
                    if last_y - center_y > self.jump_threshold:
                        # Check if this hand is different from the last jump hand
                        if self.last_jump_hand is None or self.last_jump_hand != handedness:
                            should_jump = True
                            jump_hand = handedness
                            # Set cooldown after detecting jump
                            self.jump_cooldown = self.jump_cooldown_frames
                            # Update which hand performed the jump
                            self.last_jump_hand = handedness
                            # Reset position after jump
                            self.last_hand_positions[hand_key] = {
                                'y': center_y,
                                'frames_still': 0
                            }
                            break  # Only one jump per cooldown period
                    
                    # Update position and track if hand is still
                    if movement < self.still_threshold:
                        # Hand is still, increment counter
                        self.last_hand_positions[hand_key] = {
                            'y': center_y,
                            'frames_still': frames_still + 1
                        }
                    else:
                        # Hand is moving, reset still counter
                        self.last_hand_positions[hand_key] = {
                            'y': center_y,
                            'frames_still': 0
                        }
                else:
                    # First time seeing this hand, initialize tracking
                    self.last_hand_positions[hand_key] = {
                        'y': center_y,
                        'frames_still': 0
                    }
        else:
            # Still update positions even during cooldown
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
                        
                        # Track if still
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
        
        # Clean up old hand positions (hands that are no longer detected)
        detected_keys = set(hand.get('handedness') for hand in hands if hand.get('handedness') != 'Unknown')
        keys_to_remove = [k for k in self.last_hand_positions.keys() if k not in detected_keys]
        for key in keys_to_remove:
            del self.last_hand_positions[key]
        
        return should_jump
    
    def run(self):
        """
        Main game loop.
        
        Returns:
            'main_menu' if user wants to return to main menu, None otherwise
        """
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'exit'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game.handle_jump():
                            self.sound_manager.play_jump_sound()
                    elif event.key == pygame.K_r and self.game.game_over:
                        self.game.restart()
                        self.sound_manager.play_start_sound()
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
            
            # Process hand gesture control
            if self.use_hand_control and self.cap is not None:
                self.frame_counter += 1
                if self.frame_counter % self.frame_skip == 0:
                    ret, frame = self.cap.read()
                    if ret:
                        # Flip frame horizontally for mirror effect
                        frame = cv2.flip(frame, 1)
                        # Detect hands first
                        hands_raw = self.hand_detector.detect_hands(frame)
                        
                        # Filter to ensure only one left and one right hand (max 2 hands total)
                        hands = self.filter_hands(hands_raw)
                        
                        # Check if hands were corrected
                        hands_corrected = len(hands_raw) != len(hands) or (
                            len(hands_raw) == len(hands) >= 2 and 
                            len(set(h.get('handedness') for h in hands_raw)) < 2
                        )
                        
                        # Draw detections on frame
                        frame_with_boxes = self.hand_detector.draw_detections(frame, hands)
                        
                        # Convert to Pygame surface and update game
                        frame_rgb = cv2.cvtColor(frame_with_boxes, cv2.COLOR_BGR2RGB)
                        frame_surface = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.shape[1::-1], "RGB")
                        self.game.set_webcam_frame(frame_surface)
                        
                        # Determine which hand should jump next (for alternating)
                        next_hand = None
                        if self.last_jump_hand == 'Left':
                            next_hand = 'Right'
                        elif self.last_jump_hand == 'Right':
                            next_hand = 'Left'
                        else:
                            next_hand = 'Either'  # First jump, any hand is ok
                        
                        # Update game with detected hands info and next hand
                        self.game.set_detected_hands(hands, next_hand, hands_corrected)
                        
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
        # Note: Don't quit pygame here - menu may still be running
        return None  # Game ended normally
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
    print("  ⚠️  ALTERNATING HANDS MODE - You must alternate!")
    print("  - Wave LEFT hand UP, then RIGHT hand UP, then LEFT...")
    if model_type == 'mediapipe':
        print("  - MediaPipe detects left/right hands automatically!")
    else:
        print("  ⚠️  Warning: YOLO models cannot detect left/right!")
        print("      Please use MediaPipe for alternating hand mode.")
    print("  - Press SPACE for keyboard jump (still works)")
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
