# Hand Detection - Enhanced with Left/Right Detection

## Features

- **Left/Right Hand Detection**: Using MediaPipe, the model can now distinguish between left and right hands
- **Multiple Model Support**: Choose between MediaPipe (recommended) or YOLO models
- **Visual Feedback**: Color-coded bounding boxes (Blue for left hand, Red for right hand)
- **Test Script**: Standalone testing without running the full game

## Installation

Install the required MediaPipe library:

```bash
pip install mediapipe
```

For YOLO models, make sure you have the model files downloaded (see original setup).

## Usage

### Testing with Webcam (Recommended)

Test the hand detection with your webcam:

```bash
# Using MediaPipe (default - supports left/right detection)
python test_hand_detector.py --mode webcam

# Using YOLO models (no left/right detection)
python test_hand_detector.py --mode webcam --model prn
```

**Webcam Controls:**
- Press `q` to quit
- Press `s` to save current frame
- Press `f` to toggle FPS display

### Testing with Images

Test on a single image:

```bash
# Detect hands in an image
python test_hand_detector.py --mode image --image path/to/image.jpg

# Save the result to a file
python test_hand_detector.py --mode image --image path/to/image.jpg --output result.jpg
```

### Command Line Options

```
--mode        : Test mode (webcam or image)
--model       : Model type (mediapipe, prn, tiny, v4-tiny, yolo)
--camera      : Camera device ID (default: 0)
--image       : Path to input image (for image mode)
--output      : Path to output image (for image mode)
--no-fps      : Hide FPS display (for webcam mode)
```

## Using in Your Code

```python
from hand_detector import HandDetector

# Initialize detector with MediaPipe for left/right detection
detector = HandDetector(model_type="mediapipe")

# Or use YOLO (no left/right detection)
detector = HandDetector(model_type="prn")

# Detect hands in a frame
hands = detector.detect_hands(frame)

# Each hand contains:
# - bbox: (x, y, width, height)
# - confidence: detection confidence score
# - center: (center_x, center_y)
# - handedness: 'Left' or 'Right' (only with MediaPipe)
# - landmarks: hand landmarks (only with MediaPipe)

for hand in hands:
    print(f"Detected {hand.get('handedness', 'unknown')} hand")
    print(f"Confidence: {hand['confidence']:.2f}")
    print(f"Position: {hand['center']}")

# Draw detections on frame
result_frame = detector.draw_detections(frame, hands)
```

## Color Coding

When displaying detections:
- **Blue** bounding box = Left hand
- **Red** bounding box = Right hand
- **Green** bounding box = Hand (handedness unknown - YOLO models)

## Model Comparison

| Model | Left/Right Detection | Speed | Accuracy |
|-------|---------------------|-------|----------|
| MediaPipe | ✅ Yes | Fast | High |
| YOLO (prn) | ❌ No | Medium | Medium |
| YOLO (tiny) | ❌ No | Fast | Low |
| YOLO (v4-tiny) | ❌ No | Fast | Medium |
| YOLO (yolo) | ❌ No | Slow | High |

**Recommendation**: Use MediaPipe for most applications, especially when you need to distinguish between left and right hands.

## Troubleshooting

### MediaPipe not available
If you see "MediaPipe not available", install it:
```bash
pip install mediapipe
```

### Camera not opening
Try different camera IDs:
```bash
python test_hand_detector.py --mode webcam --camera 1
```

### YOLO models not loading
Make sure you've downloaded the model files:
```bash
cd models && sh download-models.sh
```

