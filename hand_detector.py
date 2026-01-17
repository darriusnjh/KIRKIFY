import cv2
import numpy as np
from typing import Optional, Tuple, List


class HandDetector:
    def __init__(self, model_type: str = "prn"):
        """
        Initialize hand detector with YOLO model.
        
        Args:
            model_type: Type of YOLO model to use ('tiny', 'prn', 'v4-tiny', or 'yolo')
        """
        self.model_type = model_type
        self.net = None
        self.output_layers = None
        self.classes = ["hand"]
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
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
            self.model_type = "prn"
        
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
    
    def draw_detections(self, frame: np.ndarray, hands: List[dict]) -> np.ndarray:
        """
        Draw hand detections on frame.
        
        Args:
            frame: Input frame
            hands: List of detected hands
            
        Returns:
            Frame with detections drawn
        """
        result_frame = frame.copy()
        
        for hand in hands:
            x, y, w, h = hand['bbox']
            confidence = hand['confidence']
            
            # Draw bounding box
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw label
            label = f"Hand: {confidence:.2f}"
            cv2.putText(result_frame, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return result_frame
