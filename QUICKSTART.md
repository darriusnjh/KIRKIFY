# Quick Start Guide - Flappy Bird with Hand Gesture Control

## Prerequisites

Make sure you have MediaPipe installed (for best left/right hand detection):

```bash
pip install mediapipe==0.10.9
```

Or run the diagnostic to check your setup:

```bash
python diagnose_setup.py
```

## Running the Game

### Option 1: MediaPipe (Recommended - Detects Left/Right Hands)

```bash
python main.py
```

Or explicitly specify MediaPipe:

```bash
python main.py -m mediapipe
```

### Option 2: YOLO Models (No Left/Right Detection)

```bash
python main.py -m prn
```

### Option 3: Keyboard Only

```bash
python main.py --no-hand
```

## How to Play

### Hand Gesture Controls
1. **Position yourself** in front of the webcam
2. **Raise your hand** (left, right, or both!) so it's visible to the camera
3. **Wave your hand UP quickly** to make the bird jump
4. The game will show which hands are detected in the top-left corner:
   - **Blue text** = Left hand detected 👈
   - **Red text** = Right hand detected 👉
   - **Green text** = Hand detected (model doesn't support left/right)

### Keyboard Controls
- **SPACE** - Make bird jump
- **R** - Restart after game over
- **ESC** - Quit game

## Features

### MediaPipe Model Features
- ✅ Detects left and right hands separately
- ✅ Can use either hand to control
- ✅ Can detect both hands simultaneously
- ✅ Shows hand skeleton/landmarks overlay
- ✅ Real-time confidence display
- ✅ Fast and accurate tracking

### Visual Feedback
- **Webcam feed** in bottom-right corner shows:
  - Blue boxes = Left hand
  - Red boxes = Right hand
  - Hand landmarks (finger joints)
- **Hand status** in top-left corner shows:
  - Which hands are detected
  - Detection confidence percentage

## Tips for Best Performance

1. **Good lighting** - Make sure your room is well-lit
2. **Clear background** - Avoid cluttered backgrounds
3. **Hand position** - Keep hands within camera frame
4. **Distance** - Stay about 1-2 feet from camera
5. **Gesture** - Make deliberate upward movements to jump

## Troubleshooting

### "No hands detected" appears
- Move closer to the camera
- Improve lighting
- Make sure hands are clearly visible
- Try spreading fingers to help detection

### Game is laggy
- Try reducing frame processing: The game already skips frames for performance
- Close other applications
- Ensure webcam drivers are up to date

### MediaPipe not working
```bash
# Reinstall MediaPipe
pip uninstall mediapipe -y
pip install mediapipe==0.10.9

# Check if it works
python diagnose_setup.py
```

### Want to use YOLO instead
```bash
# Download YOLO models
cd models
.\download-models.ps1

# Run with YOLO
python main.py -m prn
```

## Command Line Options

```
usage: main.py [-h] [--no-hand] [-m MODEL] [-n NETWORK]

Flappy Bird with Hand Gesture Control

optional arguments:
  -h, --help            show this help message and exit
  --no-hand             Disable hand gesture control (use keyboard only)
  -m MODEL, --model MODEL
                        Hand detection model to use (default: mediapipe)
                        choices: mediapipe, tiny, prn, v4-tiny, yolo
  -n NETWORK, --network NETWORK
                        (Deprecated: use -m) YOLO model type to use
```

## Examples

```bash
# Default - MediaPipe with hand control
python main.py

# Keyboard only
python main.py --no-hand

# Use YOLO PRN model
python main.py -m prn

# Test hand detection without playing
python test_hand_detector.py --mode webcam
```

## Advanced

### Testing Hand Detection Only
Before playing the game, test if your hand detection is working:

```bash
# Test MediaPipe
python test_hand_detector.py --mode webcam --model mediapipe

# Test YOLO
python test_hand_detector.py --mode webcam --model prn
```

### System Diagnostics
Check what models are available and working:

```bash
python diagnose_setup.py
```

This will show:
- ✅ What's working
- ❌ What's not working
- 📝 How to fix any issues

Enjoy the game! 🎮🐦

