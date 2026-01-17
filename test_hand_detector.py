#!/usr/bin/env python3
"""
Test script for hand detection model.
Tests both MediaPipe (with left/right detection) and YOLO models.
"""
import cv2
import argparse
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from core.hand_detector import HandDetector


def test_webcam(model_type: str = "mediapipe", camera_id: int = 0, show_fps: bool = True):
    """
    Test hand detection using webcam.
    
    Args:
        model_type: Type of model to use ('mediapipe', 'prn', 'tiny', etc.)
        camera_id: Camera device ID
        show_fps: Whether to display FPS on screen
    """
    print(f"Initializing hand detector with model: {model_type}")
    detector = HandDetector(model_type=model_type)
    
    # Check if detector loaded successfully
    if detector.model_type == "mediapipe" and detector.hands_detector is None:
        print("\n⚠ MediaPipe failed to load and YOLO fallback may not be available")
        print("Run 'python diagnose_setup.py' to check your setup\n")
    elif detector.model_type != "mediapipe" and detector.net is None:
        print(f"\n✗ {detector.model_type} model failed to load")
        print("Run 'python diagnose_setup.py' to check your setup\n")
        return
    
    print(f"Opening camera {camera_id}...")
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_id}")
        return
    
    print("Camera opened successfully!")
    print("\nControls:")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save current frame")
    print("  - Press 'f' to toggle FPS display")
    print("\nStarting detection...")
    
    frame_count = 0
    start_time = time.time()
    fps = 0
    show_fps_flag = show_fps
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Flip frame horizontally for mirror view
        frame = cv2.flip(frame, 1)
        
        # Detect hands
        detection_start = time.time()
        hands = detector.detect_hands(frame)
        detection_time = time.time() - detection_start
        
        # Draw detections
        result_frame = detector.draw_detections(frame, hands)
        
        # Calculate FPS
        frame_count += 1
        if frame_count % 10 == 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
        
        # Display info on frame
        info_y = 30
        cv2.putText(result_frame, f"Model: {model_type}", (10, info_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if show_fps_flag:
            info_y += 30
            cv2.putText(result_frame, f"FPS: {fps:.1f}", (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            info_y += 25
            cv2.putText(result_frame, f"Detection time: {detection_time*1000:.1f}ms", (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        info_y += 30
        cv2.putText(result_frame, f"Hands detected: {len(hands)}", (10, info_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Display hand details
        for i, hand in enumerate(hands):
            info_y += 25
            handedness = hand.get('handedness', 'Unknown')
            confidence = hand['confidence']
            text = f"  Hand {i+1}: {handedness} ({confidence:.2f})"
            cv2.putText(result_frame, text, (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Show frame
        cv2.imshow('Hand Detection Test', result_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nQuitting...")
            break
        elif key == ord('s'):
            filename = f"hand_detection_{int(time.time())}.jpg"
            cv2.imwrite(filename, result_frame)
            print(f"Saved frame to {filename}")
        elif key == ord('f'):
            show_fps_flag = not show_fps_flag
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Test completed!")


def test_image(image_path: str, model_type: str = "mediapipe", output_path: str = None):
    """
    Test hand detection on a single image.
    
    Args:
        image_path: Path to input image
        model_type: Type of model to use
        output_path: Path to save output image (optional)
    """
    print(f"Initializing hand detector with model: {model_type}")
    detector = HandDetector(model_type=model_type)
    
    print(f"Loading image: {image_path}")
    frame = cv2.imread(image_path)
    
    if frame is None:
        print(f"Error: Could not load image from {image_path}")
        return
    
    print("Detecting hands...")
    hands = detector.detect_hands(frame)
    
    print(f"Found {len(hands)} hand(s)")
    for i, hand in enumerate(hands):
        handedness = hand.get('handedness', 'Unknown')
        confidence = hand['confidence']
        print(f"  Hand {i+1}: {handedness} (confidence: {confidence:.2f})")
    
    # Draw detections
    result_frame = detector.draw_detections(frame, hands)
    
    # Save or display
    if output_path:
        cv2.imwrite(output_path, result_frame)
        print(f"Saved result to: {output_path}")
    else:
        cv2.imshow('Hand Detection Result', result_frame)
        print("Press any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description='Test hand detection model')
    parser.add_argument('--mode', type=str, default='webcam', choices=['webcam', 'image'],
                       help='Test mode: webcam or image')
    parser.add_argument('--model', type=str, default='mediapipe',
                       choices=['mediapipe', 'prn', 'tiny', 'v4-tiny', 'yolo'],
                       help='Model type to use')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera device ID (for webcam mode)')
    parser.add_argument('--image', type=str,
                       help='Path to input image (for image mode)')
    parser.add_argument('--output', type=str,
                       help='Path to output image (for image mode)')
    parser.add_argument('--no-fps', action='store_true',
                       help='Hide FPS display (for webcam mode)')
    
    args = parser.parse_args()
    
    if args.mode == 'webcam':
        test_webcam(
            model_type=args.model,
            camera_id=args.camera,
            show_fps=not args.no_fps
        )
    elif args.mode == 'image':
        if not args.image:
            print("Error: --image is required for image mode")
            return
        test_image(
            image_path=args.image,
            model_type=args.model,
            output_path=args.output
        )


if __name__ == "__main__":
    main()

