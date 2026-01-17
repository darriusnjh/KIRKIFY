import pygame
import cv2
import sys
from counting_game import CountingGame
from hand_detector import HandDetector
from sound_manager import SoundManager


class CountingGameController:
    """Controller for the counting game with hand gesture detection."""
    
    def __init__(self, model_type: str = "mediapipe", screen_width: int = 800, screen_height: int = 600):
        """
        Initialize counting game controller.
        
        Args:
            model_type: Model type for hand detection ('mediapipe', 'tiny', 'prn', etc.)
            screen_width: Screen width
            screen_height: Screen height
        """
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Counting Game - 67 Games")
        self.clock = pygame.time.Clock()
        
        self.sound_manager = SoundManager()
        self.game = CountingGame(sound_manager=self.sound_manager, 
                                 screen_width=screen_width, 
                                 screen_height=screen_height)
        self.game.set_screen(self.screen)
        
        # Hand detection
        print(f"Initializing hand detector with {model_type} model...")
        self.hand_detector = HandDetector(model_type=model_type)
        
        # Check if detector loaded successfully
        if model_type == "mediapipe":
            if self.hand_detector.hands_detector is None:
                print("Warning: MediaPipe failed to load. Trying YOLO fallback...")
                if self.hand_detector.net is None:
                    print("Warning: No working hand detection model. Game will not work.")
                    self.hand_detector = None
                    self.cap = None
                    return
        elif self.hand_detector.net is None:
            print("Warning: Hand detection model failed to load. Game will not work.")
            self.hand_detector = None
            self.cap = None
            return
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Warning: Could not open webcam.")
            self.cap = None
        
        self.running = True
        self.last_hand_y = {'left': None, 'right': None}
        self.movement_threshold = 30  # pixels of movement to detect gesture
        self.frame_skip = 2
        self.frame_counter = 0
        
        # Track hand movement states for up/down detection
        self.hand_movement_states = {
            'left': {'direction': None, 'last_y': None, 'peak_y': None, 'valley_y': None},
            'right': {'direction': None, 'last_y': None, 'peak_y': None, 'valley_y': None}
        }
    
    def detect_alternating_gesture(self, frame):
        """
        Detect alternating hand gestures with up and down movements.
        Returns actions like 'left_up', 'left_down', 'right_up', 'right_down'
        """
        if not self.hand_detector or not self.cap:
            return None
        
        hands = self.hand_detector.detect_hands(frame)
        
        if len(hands) == 0:
            # Reset tracking when no hands detected
            for hand in ['left', 'right']:
                self.hand_movement_states[hand]['last_y'] = None
            return None
        
        # Find left and right hands
        left_hand = None
        right_hand = None
        
        for hand in hands:
            handedness = hand.get('handedness', None)
            if handedness:
                if handedness == 'Left':
                    left_hand = hand
                elif handedness == 'Right':
                    right_hand = hand
        
        # If no handedness info (YOLO), use position
        if not left_hand and not right_hand and len(hands) > 0:
            frame_width = frame.shape[1]
            for hand in hands:
                center_x = hand['center'][0]
                if center_x < frame_width // 2:
                    left_hand = hand
                else:
                    right_hand = hand
        
        actions = []
        
        # Detect movement for left hand
        if left_hand:
            center_y = left_hand['center'][1]
            state = self.hand_movement_states['left']
            
            # Initialize if first detection
            if state['last_y'] is None:
                state['last_y'] = center_y
            else:
                delta_y = state['last_y'] - center_y  # Positive = moved up, Negative = moved down
                
                if abs(delta_y) > self.movement_threshold:
                    if delta_y > 0:  # Moving up
                        if state['direction'] != 'up':
                            state['direction'] = 'up'
                            state['valley_y'] = state['last_y']  # Record the low point
                            actions.append('left_up')
                        # Update peak if we're going higher
                        if state['peak_y'] is None or center_y < state['peak_y']:
                            state['peak_y'] = center_y
                    else:  # Moving down
                        if state['direction'] == 'up':  # Was going up, now going down
                            state['direction'] = 'down'
                            actions.append('left_down')
                        # Update valley if we're going lower
                        if state['valley_y'] is None or center_y > state['valley_y']:
                            state['valley_y'] = center_y
                
                state['last_y'] = center_y
        
        # Detect movement for right hand
        if right_hand:
            center_y = right_hand['center'][1]
            state = self.hand_movement_states['right']
            
            # Initialize if first detection
            if state['last_y'] is None:
                state['last_y'] = center_y
            else:
                delta_y = state['last_y'] - center_y  # Positive = moved up, Negative = moved down
                
                if abs(delta_y) > self.movement_threshold:
                    if delta_y > 0:  # Moving up
                        if state['direction'] != 'up':
                            state['direction'] = 'up'
                            state['valley_y'] = state['last_y']  # Record the low point
                            actions.append('right_up')
                        # Update peak if we're going higher
                        if state['peak_y'] is None or center_y < state['peak_y']:
                            state['peak_y'] = center_y
                    else:  # Moving down
                        if state['direction'] == 'up':  # Was going up, now going down
                            state['direction'] = 'down'
                            actions.append('right_down')
                        # Update valley if we're going lower
                        if state['valley_y'] is None or center_y > state['valley_y']:
                            state['valley_y'] = center_y
                
                state['last_y'] = center_y
        
        # Return the first action detected (or None)
        return actions[0] if actions else None
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game.game_over:
                        self.game.reset()
                        if self.sound_manager:
                            self.sound_manager.play_start_sound()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Process hand gesture control and display camera feed
            if self.cap is not None:
                ret, frame = self.cap.read()
                if ret:
                    # Flip frame horizontally for mirror effect
                    frame = cv2.flip(frame, 1)
                    
                    # Always update camera feed for display
                    # Detect hands for display
                    hands = self.hand_detector.detect_hands(frame)
                    
                    # Draw detections on frame
                    frame_with_detections = self.hand_detector.draw_detections(frame, hands)
                    
                    # Convert to Pygame surface
                    frame_rgb = cv2.cvtColor(frame_with_detections, cv2.COLOR_BGR2RGB)
                    frame_surface = pygame.image.frombuffer(
                        frame_rgb.tobytes(), 
                        frame_rgb.shape[1::-1], 
                        "RGB"
                    )
                    
                    # Set webcam frame in game (always update for smooth display)
                    self.game.set_webcam_frame(frame_surface)
                    
                    # Detect gesture (only process every Nth frame for performance)
                    self.frame_counter += 1
                    if self.frame_counter % self.frame_skip == 0:
                        gesture = self.detect_alternating_gesture(frame)
                        if gesture:
                            self.game.handle_action(gesture)
            
            # Update game
            self.game.update()
            
            # Update sound manager (for music restoration after count sound)
            self.sound_manager.update()
            
            # Draw game
            self.game.draw()
            
            self.clock.tick(60)
        
        # Cleanup
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        # Note: Don't quit pygame here - menu may still be running
