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

### ⚠️ ALTERNATING HANDS MODE (NEW!)
The game now requires you to **alternate between left and right hands**!

1. **Position yourself** in front of the webcam with **both hands visible**
2. **Wave LEFT hand UP** to jump
3. **Wave RIGHT hand UP** for the next jump
4. **Continue alternating**: LEFT → RIGHT → LEFT → RIGHT...
5. Watch the **BIG indicator** at the top of screen:
   - 🔵 **"Wave LEFT Hand!"** = Use left hand
   - 🔴 **"Wave RIGHT Hand!"** = Use right hand
   - 🟡 **"Wave Either Hand!"** = First jump, any hand works

**Note**: Waving the same hand twice won't work - you MUST alternate!

See [ALTERNATING_MODE.md](ALTERNATING_MODE.md) for detailed guide and strategies.

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
5. **Gesture** - Make **quick upward movements** to jump (more sensitive now!)

### ⚡ Performance Optimizations
The game is now tuned for **maximum sensitivity and responsiveness**:
- **Jump threshold**: 15 pixels (was 30) - smaller movements trigger jumps
- **Frame processing**: Every frame (was every 2nd) - instant response
- **Detection confidence**: 0.3 (was 0.5) - easier hand detection
- **Smart cooldown**: 5 frames (~0.08s) prevents accidental double-jumps

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

