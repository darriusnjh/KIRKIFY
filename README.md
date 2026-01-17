# Flappy Bird with Hand Gesture Control

A Flappy Bird game implementation in Python with hand gesture control using YOLO hand detection. Control the bird by waving your hand in front of the webcam!

## Features

- 🎮 Classic Flappy Bird gameplay
- ✋ Hand gesture control via webcam (using YOLO hand detection)
- ⌨️ Keyboard control (SPACE to jump, R to restart)
- 🎵 Soundtrack and sound effects support
- 🏆 High score tracking
- 🎨 Authentic Flappy Bird UI and graphics

## Requirements

- Python 3.7+
- Webcam (for hand gesture control)
- OpenCV
- Pygame
- NumPy

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download YOLO hand detection models:

**On macOS/Linux:**
```bash
cd models
sh download-models.sh
```

**On Windows:**
```powershell
cd models
powershell .\download-models.ps1
```

**Note:** If the automatic download fails, you can manually download the models from:
https://github.com/cansik/yolo-hand-detection/releases

Place the `.weights` and `.cfg` files in the `models/` directory.

## Usage

### Run with Hand Gesture Control (Default)

```bash
python main.py
```

### Run with Different YOLO Model

```bash
# Use YOLOv3-tiny (fastest, default)
python main.py -n tiny

# Use YOLOv3-tiny-PRN (better accuracy)
python main.py -n prn

# Use YOLOv4-tiny (best accuracy)
python main.py -n v4-tiny

# Use YOLOv3 full (slowest, most accurate)
python main.py -n yolo
```

### Run with Keyboard Only

```bash
python main.py --no-hand
```

## Controls

### Hand Gesture Control
- Wave your hand upward in front of the webcam to make the bird jump
- The game detects upward hand movement to trigger jumps

### Keyboard Control
- **SPACE**: Jump/Start game
- **R**: Restart after game over
- **ESC**: Quit game

## Adding Sound Effects and Music

### Sound Effects
Place sound effect files in the `sounds/` directory:
- `jump.wav` - Played when bird jumps
- `hit.wav` - Played on collision
- `score.wav` - Played when passing a pipe

### Background Music
Place background music files in the `music/` directory:
- `background.mp3`, `background.wav`, or `background.ogg`
- Or any `.mp3`, `.wav`, or `.ogg` file (first one found will be used)

The game will automatically detect and play these files if present.

## High Scores

High scores are automatically saved to `high_scores.json` in the project root. The file is created automatically on first run.

## Project Structure

```
KIRKIFY/
├── main.py              # Main game controller and entry point
├── game.py              # Flappy Bird game logic
├── hand_detector.py     # YOLO hand detection integration
├── sound_manager.py     # Sound effects and music management
├── requirements.txt     # Python dependencies
├── models/              # YOLO model files (download required)
│   ├── download-models.sh
│   └── download-models.ps1
├── sounds/              # Sound effects (optional)
├── music/               # Background music (optional)
└── high_scores.json     # High score storage (auto-generated)
```

## Hand Detection Model

This project uses the YOLO hand detection model from [cansik/yolo-hand-detection](https://github.com/cansik/yolo-hand-detection).

The model detects hands in real-time from webcam input and triggers game actions based on hand movement gestures.

## Troubleshooting

### Webcam Not Working
- Make sure your webcam is connected and not being used by another application
- The game will automatically fall back to keyboard control if webcam fails to open

### Models Not Found
- Run the download script in the `models/` directory
- Make sure `.weights` and `.cfg` files are present for your chosen model type

### Performance Issues
- Use `-n tiny` for fastest performance (YOLOv3-tiny)
- Reduce frame processing by adjusting `frame_skip` in `main.py`
- Close other applications using the webcam

## License

This project uses the YOLO hand detection model from cansik/yolo-hand-detection. Please refer to the original repository for model licensing information.

## Credits

- YOLO Hand Detection: [cansik/yolo-hand-detection](https://github.com/cansik/yolo-hand-detection)
- Game inspired by Flappy Bird by Dong Nguyen
