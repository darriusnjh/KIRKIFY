#!/usr/bin/env python3
"""
Diagnostic script to check if all dependencies are working correctly.
"""
import sys
import os

def check_opencv():
    """Check if OpenCV is installed and working."""
    try:
        import cv2
        print(f"[OK] OpenCV installed: version {cv2.__version__}")
        
        # Test camera access
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("[OK] Camera access working")
            cap.release()
        else:
            print("[FAIL] Camera could not be opened")
        return True
    except ImportError as e:
        print(f"[FAIL] OpenCV not installed: {e}")
        return False

def check_mediapipe():
    """Check if MediaPipe is installed and working."""
    try:
        import mediapipe as mp
        print(f"[OK] MediaPipe installed: version {mp.__version__}")
        
        # Check if solutions is available
        if hasattr(mp, 'solutions'):
            print("[OK] MediaPipe solutions available")
            
            # Try to initialize hands
            try:
                mp_hands = mp.solutions.hands
                hands = mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.5
                )
                print("[OK] MediaPipe Hands initialized successfully")
                hands.close()
                return True
            except Exception as e:
                print(f"[FAIL] Error initializing MediaPipe Hands: {e}")
                return False
        else:
            print("[FAIL] MediaPipe solutions not available")
            print("  This usually means MediaPipe is corrupted or incompletely installed")
            return False
            
    except ImportError as e:
        print(f"[FAIL] MediaPipe not installed: {e}")
        return False

def check_numpy():
    """Check if NumPy is installed."""
    try:
        import numpy as np
        print(f"[OK] NumPy installed: version {np.__version__}")
        return True
    except ImportError as e:
        print(f"[FAIL] NumPy not installed: {e}")
        return False

def check_yolo_models():
    """Check if YOLO model files exist."""
    model_dir = "models"
    models_to_check = [
        ("yolov3-tiny-prn.cfg", "yolov3-tiny-prn.weights"),
    ]
    
    all_found = True
    for cfg, weights in models_to_check:
        cfg_path = os.path.join(model_dir, cfg)
        weights_path = os.path.join(model_dir, weights)
        
        if os.path.exists(cfg_path) and os.path.exists(weights_path):
            print(f"[OK] YOLO model found: {cfg.replace('.cfg', '')}")
        else:
            print(f"[FAIL] YOLO model missing: {cfg.replace('.cfg', '')}")
            all_found = False
    
    return all_found

def main():
    print("=" * 50)
    print("Hand Detection Setup Diagnostics")
    print("=" * 50)
    print()
    
    print("Checking dependencies...")
    print("-" * 50)
    
    opencv_ok = check_opencv()
    print()
    
    numpy_ok = check_numpy()
    print()
    
    mediapipe_ok = check_mediapipe()
    print()
    
    print("Checking YOLO models...")
    print("-" * 50)
    yolo_ok = check_yolo_models()
    print()
    
    print("=" * 50)
    print("Summary")
    print("=" * 50)
    
    if mediapipe_ok:
        print("[OK] You can use MediaPipe for left/right hand detection!")
        print("  Run: python test_hand_detector.py --mode webcam --model mediapipe")
    elif yolo_ok:
        print("[WARN] MediaPipe not working, but YOLO is available")
        print("  Run: python test_hand_detector.py --mode webcam --model prn")
    else:
        print("[FAIL] No working hand detection models found")
        
    print()
    
    if not mediapipe_ok:
        print("To fix MediaPipe:")
        print("  pip uninstall mediapipe -y")
        print("  pip install mediapipe==0.10.9")
    
    if not yolo_ok:
        print("To download YOLO models:")
        print("  cd models && sh download-models.sh")

if __name__ == "__main__":
    main()
