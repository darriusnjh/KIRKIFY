import cv2
import numpy as np
from typing import Optional, Tuple, List

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available. Install with: pip install mediapipe")


class HandDetector:
    def __init__(self, model_type: str = "mediapipe", detect_hands_lr: bool = True):
        """
        Initialize hand detector.
        
        Args:
            model_type: Type of model to use ('mediapipe', 'tiny', 'prn', 'v4-tiny', or 'yolo')
            detect_hands_lr: If True, detect left/right hands (only works with 'mediapipe')
        """
        self.model_type = model_type
        self.detect_hands_lr = detect_hands_lr
        self.net = None
        self.output_layers = None
        self.classes = ["hand"]
        self.confidence_threshold = 0.2  # Reduced from 0.5 for more sensitive detection
        self.nms_threshold = 0.4
        
        # MediaPipe setup
        self.mp_hands = None
        self.hands_detector = None
        
        self.load_model()
        
    def load_model(self):
        """Load hand detection model."""
        if self.model_type == "mediapipe":
            if not MEDIAPIPE_AVAILABLE:
                print("⚠ MediaPipe not available. Falling back to YOLO.")
                self.model_type = "prn"
            else:
                try:
                    # Check if mp.solutions is available
                    if not hasattr(mp, 'solutions'):
                        print("⚠ MediaPipe is installed but 'solutions' module is not available.")
                        print("  This usually means MediaPipe is corrupted.")
                        print("  Try: pip uninstall mediapipe -y && pip install mediapipe==0.10.9")
                        print("  Falling back to YOLO...")
                        self.model_type = "prn"
                    else:
                        self.mp_hands = mp.solutions.hands
                        self.hands_detector = self.mp_hands.Hands(
                            static_image_mode=False,
                            max_num_hands=2,
                            min_detection_confidence=0.3,  # Reduced from 0.5 for more sensitivity
                            min_tracking_confidence=0.3    # Reduced from 0.5 for better tracking
                        )
                        print("✓ Successfully loaded MediaPipe hand detector")
                        return
                except Exception as e:
                    print(f"⚠ Error loading MediaPipe: {e}")
                    print("  Falling back to YOLO...")
                    self.model_type = "prn"
        
        # YOLO model loading
        model_dir = "models"
        
        # Map model types to file names
        model_files = {
            "tiny": ("yolov3-tiny.cfg", "yolov3-tiny.weights"),
            "prn": ("yolov3-tiny-prn.cfg", "yolov3-tiny-prn.weights"),
            "v4-tiny": ("yolov4-tiny.cfg", "yolov4-tiny.weights"),
            "yolo": ("yolov3.cfg", "yolov3.weights")
        }
        
        if self.model_type not in model_files:
            print(f"Unknown model type: {self.model_type}. Using 'prn' instead.")
            self.model_type = "prn"
        
        cfg_file, weights_file = model_files[self.model_type]
        cfg_path = f"{model_dir}/{cfg_file}"
        weights_path = f"{model_dir}/{weights_file}"
        
        try:
            import os
            if not os.path.exists(cfg_path) or not os.path.exists(weights_path):
                print(f"✗ YOLO model files not found:")
                print(f"  Looking for: {cfg_path}")
                print(f"  Looking for: {weights_path}")
                print("  Please download models: cd models && sh download-models.sh")
                self.net = None
                return
                
            self.net = cv2.dnn.readNet(weights_path, cfg_path)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            # Get output layer names
            layer_names = self.net.getLayerNames()
            self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            
            print(f"✓ Successfully loaded {self.model_type} YOLO model")
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            print("  Please make sure models are downloaded. Run: cd models && sh download-models.sh")
            self.net = None
    
    def detect_hands(self, frame: np.ndarray) -> List[dict]:
        """
        Detect hands in a frame.
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of detected hands with bounding boxes, confidence scores, and handedness (if available)
            Each hand dict contains: 'bbox', 'confidence', 'center', and optionally 'handedness' ('Left' or 'Right')
        """
        if self.model_type == "mediapipe" and self.hands_detector is not None:
            return self._detect_hands_mediapipe(frame)
        else:
            return self._detect_hands_yolo(frame)
    
    def _detect_hands_mediapipe(self, frame: np.ndarray) -> List[dict]:
        """Detect hands using MediaPipe with left/right classification."""
        height, width = frame.shape[:2]
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands_detector.process(rgb_frame)
        
        hands = []
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Get bounding box from landmarks
                x_coords = [lm.x for lm in hand_landmarks.landmark]
                y_coords = [lm.y for lm in hand_landmarks.landmark]
                
                x_min = int(min(x_coords) * width)
                y_min = int(min(y_coords) * height)
                x_max = int(max(x_coords) * width)
                y_max = int(max(y_coords) * height)
                
                # Add some padding
                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(width, x_max + padding)
                y_max = min(height, y_max + padding)
                
                w = x_max - x_min
                h = y_max - y_min
                
                # Get handedness (Left or Right)
                hand_label = handedness.classification[0].label
                confidence = handedness.classification[0].score
                
                hands.append({
                    'bbox': (x_min, y_min, w, h),
                    'confidence': confidence,
                    'center': (x_min + w // 2, y_min + h // 2),
                    'handedness': hand_label,
                    'landmarks': hand_landmarks
                })
        
        return hands
    
    def _detect_hands_yolo(self, frame: np.ndarray) -> List[dict]:
        """Detect hands using YOLO (no left/right classification)."""
        if self.net is None:
            return []
        
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)
        
        boxes = []
        confidences = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.confidence_threshold:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
        
        # Apply non-maximum suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
        
        hands = []
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                hands.append({
                    'bbox': (x, y, w, h),
                    'confidence': confidences[i],
                    'center': (x + w // 2, y + h // 2)
                })
        
        return hands
    
    def detect_gesture(self, frame: np.ndarray) -> Optional[str]:
        """
        Detect hand gesture for game control.
        Simple gesture: if hand moves upward quickly, it's a jump gesture.
        
        Args:
            frame: Input image frame
            
        Returns:
            'jump' if upward gesture detected, None otherwise
        """
        hands = self.detect_hands(frame)
        
        if len(hands) > 0:
            # Get the hand with highest confidence
            hand = max(hands, key=lambda h: h['confidence'])
            return 'jump'
        
        return None
    
    def __del__(self):
        """Clean up resources."""
        if self.hands_detector is not None:
            self.hands_detector.close()
    
    def draw_detections(self, frame: np.ndarray, hands: List[dict]) -> np.ndarray:
        """
        Draw hand detections on frame as simple colored circles/balls.
        Always shows both left and right hand positions (solid circles, dimmer when not detected).
        
        Args:
            frame: Input frame
            hands: List of detected hands
            
        Returns:
            Frame with detections drawn as circles
        """
        result_frame = frame.copy()
        height, width = frame.shape[:2]
        
        # Default radius for balls
        default_radius = 50
        
        # Fixed positions for undetected hands
        left_default_pos = (width // 4, height // 2)
        right_default_pos = (3 * width // 4, height // 2)
        
        # Track which hands are detected
        left_hand_detected = None
        right_hand_detected = None
        
        for hand in hands:
            handedness = hand.get('handedness', None)
            if handedness == 'Left':
                left_hand_detected = hand
            elif handedness == 'Right':
                right_hand_detected = hand
        
        # Draw left hand (detected or ghost)
        if left_hand_detected:
            # Draw actual detected left hand
            x, y, w, h = left_hand_detected['bbox']
            center = left_hand_detected['center']
            radius = min(w, h) // 2
            radius = max(30, min(radius, 80))
            color = (255, 0, 0)  # Blue for left (BGR)
            
            # Draw filled circle
            cv2.circle(result_frame, center, radius, color, -1)
            # Draw white outline
            cv2.circle(result_frame, center, radius, (255, 255, 255), 4)
        else:
            # Draw solid left hand (dimmer when not detected)
            color = (180, 0, 0)  # Dimmer blue
            # Draw filled circle (always solid, not ghost)
            cv2.circle(result_frame, left_default_pos, default_radius, color, -1)
            # Draw white outline
            cv2.circle(result_frame, left_default_pos, default_radius, (255, 255, 255), 4)
            
        # Draw label for left hand
        label = "L"
        font_scale = 2.0
        thickness = 4
        center_to_use = left_hand_detected['center'] if left_hand_detected else left_default_pos
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        text_x = center_to_use[0] - text_size[0] // 2
        text_y = center_to_use[1] + text_size[1] // 2
        
        # Draw text shadow
        cv2.putText(result_frame, label, (text_x + 3, text_y + 3),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness + 2)
        # Draw text (slightly dimmer when not detected)
        text_color = (255, 255, 255) if left_hand_detected else (200, 200, 200)
        cv2.putText(result_frame, label, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
        
        # Draw right hand (detected or ghost)
        if right_hand_detected:
            # Draw actual detected right hand
            x, y, w, h = right_hand_detected['bbox']
            center = right_hand_detected['center']
            radius = min(w, h) // 2
            radius = max(30, min(radius, 80))
            color = (0, 0, 255)  # Red for right (BGR)
            
            # Draw filled circle
            cv2.circle(result_frame, center, radius, color, -1)
            # Draw white outline
            cv2.circle(result_frame, center, radius, (255, 255, 255), 4)
        else:
            # Draw solid right hand (dimmer when not detected)
            color = (0, 0, 180)  # Dimmer red
            # Draw filled circle (always solid, not ghost)
            cv2.circle(result_frame, right_default_pos, default_radius, color, -1)
            # Draw white outline
            cv2.circle(result_frame, right_default_pos, default_radius, (255, 255, 255), 4)
        
        # Draw label for right hand
        label = "R"
        center_to_use = right_hand_detected['center'] if right_hand_detected else right_default_pos
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        text_x = center_to_use[0] - text_size[0] // 2
        text_y = center_to_use[1] + text_size[1] // 2
        
        # Draw text shadow
        cv2.putText(result_frame, label, (text_x + 3, text_y + 3),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness + 2)
        # Draw text (slightly dimmer when not detected)
        text_color = (255, 255, 255) if right_hand_detected else (200, 200, 200)
        cv2.putText(result_frame, label, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
        
        return result_frame
