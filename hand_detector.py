import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict
from collections import deque


class HandDetector:
    def __init__(self, model_type: str = "tiny", history_size: int = 10):
        """
        Initialize hand detector with YOLO model.
        
        Args:
            model_type: Type of YOLO model to use ('tiny', 'prn', 'v4-tiny', or 'yolo')
            history_size: Number of frames to keep in position history
        """
        self.model_type = model_type
        self.net = None
        self.output_layers = None
        self.classes = ["hand"]
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        self.history_size = history_size
        
        # Track hand positions over time
        self.left_hand_history = deque(maxlen=history_size)
        self.right_hand_history = deque(maxlen=history_size)
        
        self.load_model()
        
    def load_model(self):
        """Load YOLO model and weights."""
        model_dir = "models"
        
        # Map model types to file names
        model_files = {
            "tiny": ("yolov3-tiny.cfg", "yolov3-tiny.weights"),
            "prn": ("yolov3-tiny-prn.cfg", "yolov3-tiny-prn.weights"),
            "v4-tiny": ("yolov4-tiny.cfg", "yolov4-tiny.weights"),
            "yolo": ("yolov3.cfg", "yolov3.weights")
        }
        
        if self.model_type not in model_files:
            print(f"Unknown model type: {self.model_type}. Using 'tiny' instead.")
            self.model_type = "tiny"
        
        cfg_file, weights_file = model_files[self.model_type]
        cfg_path = f"{model_dir}/{cfg_file}"
        weights_path = f"{model_dir}/{weights_file}"
        
        try:
            self.net = cv2.dnn.readNet(weights_path, cfg_path)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            # Get output layer names
            layer_names = self.net.getLayerNames()
            self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            
            print(f"Successfully loaded {self.model_type} model")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Please make sure models are downloaded. Run: cd models && sh download-models.sh")
            self.net = None
    
    def detect_hands(self, frame: np.ndarray) -> List[dict]:
        """
        Detect hands in a frame.
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of detected hands with bounding boxes and confidence scores
        """
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
    
    def identify_hands(self, hands: List[dict], frame_width: int) -> Dict[str, Optional[dict]]:
        """
        Identify which hand is left and which is right based on position.
        
        Args:
            hands: List of detected hands
            frame_width: Width of the frame
            
        Returns:
            Dictionary with 'left' and 'right' hand positions
        """
        if len(hands) == 0:
            return {'left': None, 'right': None}
        
        if len(hands) == 1:
            # If only one hand, determine side based on position
            hand = hands[0]
            center_x = hand['center'][0]
            if center_x < frame_width // 2:
                return {'left': hand, 'right': None}
            else:
                return {'left': None, 'right': hand}
        
        # If two hands, sort by x position (left to right)
        sorted_hands = sorted(hands, key=lambda h: h['center'][0])
        return {'left': sorted_hands[0], 'right': sorted_hands[1]}
    
    def detect_dual_hand_gesture(self, frame: np.ndarray, movement_threshold: int = 30) -> bool:
        """
        Detect dual-hand gesture: one hand goes up while the other goes down.
        This counts as one jump action.
        
        Args:
            frame: Input image frame
            movement_threshold: Minimum pixels of movement to detect gesture
            
        Returns:
            True if the alternating up/down gesture is detected, False otherwise
        """
        hands = self.detect_hands(frame)
        
        if len(hands) < 2:
            # Need both hands for this gesture
            self.left_hand_history.clear()
            self.right_hand_history.clear()
            return False
        
        frame_width = frame.shape[1]
        identified = self.identify_hands(hands, frame_width)
        
        left_hand = identified['left']
        right_hand = identified['right']
        
        # Update history for both hands
        if left_hand:
            self.left_hand_history.append(left_hand['center'][1])  # y position
        else:
            self.left_hand_history.clear()
        
        if right_hand:
            self.right_hand_history.append(right_hand['center'][1])  # y position
        else:
            self.right_hand_history.clear()
        
        # Need enough history to detect movement
        if len(self.left_hand_history) < 3 or len(self.right_hand_history) < 3:
            return False
        
        # Get recent positions
        left_recent = list(self.left_hand_history)[-3:]
        right_recent = list(self.right_hand_history)[-3:]
        
        # Calculate movement direction
        # Negative delta_y means moving up (y decreases), positive means moving down
        left_delta = left_recent[0] - left_recent[-1]  # Positive = moved up
        right_delta = right_recent[0] - right_recent[-1]  # Positive = moved up
        
        # Check for alternating pattern:
        # Pattern 1: Left goes up AND Right goes down
        # Pattern 2: Right goes up AND Left goes down
        pattern1 = (left_delta > movement_threshold and 
                   right_delta < -movement_threshold)
        pattern2 = (right_delta > movement_threshold and 
                   left_delta < -movement_threshold)
        
        if pattern1 or pattern2:
            # Clear history after detecting gesture to prevent multiple triggers
            self.left_hand_history.clear()
            self.right_hand_history.clear()
            return True
        
        return False
    
    def detect_gesture(self, frame: np.ndarray) -> Optional[str]:
        """
        Detect hand gesture for game control.
        Simple gesture: if hand moves upward quickly, it's a jump gesture.
        (Kept for backward compatibility, but dual-hand gesture is preferred)
        
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
    
    def draw_detections(self, frame: np.ndarray, hands: List[dict], 
                       identified_hands: Optional[Dict[str, Optional[dict]]] = None) -> np.ndarray:
        """
        Draw hand detections on frame with left/right labels.
        
        Args:
            frame: Input frame
            hands: List of detected hands
            identified_hands: Optional dictionary with 'left' and 'right' hand positions
            
        Returns:
            Frame with detections drawn
        """
        result_frame = frame.copy()
        frame_width = frame.shape[1]
        
        if identified_hands is None:
            identified_hands = self.identify_hands(hands, frame_width)
        
        for hand in hands:
            x, y, w, h = hand['bbox']
            confidence = hand['confidence']
            
            # Determine if this is left or right hand
            if identified_hands['left'] and hand == identified_hands['left']:
                color = (255, 0, 0)  # Blue for left
                label = f"Left: {confidence:.2f}"
            elif identified_hands['right'] and hand == identified_hands['right']:
                color = (0, 0, 255)  # Red for right
                label = f"Right: {confidence:.2f}"
            else:
                color = (0, 255, 0)  # Green for unidentified
                label = f"Hand: {confidence:.2f}"
            
            # Draw bounding box
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            cv2.putText(result_frame, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return result_frame
