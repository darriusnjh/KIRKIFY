# 67 Games

A collection of hand gesture-controlled games using computer vision.

## Games Available

### 1. Flappy Bird
Classic Flappy Bird game controlled by alternating hand gestures. Wave your left hand, then right hand, then left... to make the bird jump!

### 2. Counting Game
Count how many alternating hand gestures you can do in 30 seconds! Challenge yourself to beat your high score.

## Running the Games

### Launch the Menu
```bash
python game_launcher.py
```

This will show a menu where you can select which game to play.

### Launch a Game Directly
```bash
# Launch Flappy Bird
python game_launcher.py --game flappy

# Launch Counting Game
python game_launcher.py --game counting
```

### Options
```bash
# Use a specific hand detection model
python game_launcher.py -m mediapipe  # or tiny, prn, v4-tiny, yolo

# Disable hand control (keyboard only)
python game_launcher.py --no-hand
```

## Counting Game Rules

1. **30 Second Timer**: You have exactly 30 seconds to count as many gestures as possible
2. **Alternating Hands**: You must alternate between left and right hands
   - First gesture can be either hand
   - After that, you must alternate (left → right → left → right...)
3. **Scoring**: Each valid alternating gesture counts as +1
4. **High Score**: Your best score is automatically saved

## Controls

### Menu Navigation
- **UP/DOWN Arrow Keys**: Navigate between games
- **ENTER/SPACE**: Select a game
- **ESC**: Exit

### In-Game Controls
- **Hand Gestures**: Wave your hand up to perform actions
- **R**: Restart game (when game over)
- **ESC**: Return to menu

## High Scores

High scores are saved in `high_scores.json`:
- `counting_game`: Best count in counting game
- `flappy_bird`: Best score in Flappy Bird (if implemented)

## Requirements

See `requirements.txt` for all dependencies. Key requirements:
- Python 3.7+
- Pygame
- OpenCV
- MediaPipe (recommended) or YOLO models
- Webcam

## Installation

```bash
pip install -r requirements.txt

# Download YOLO models (if not using MediaPipe)
cd models && sh download-models.sh
```

## Adding New Games

To add a new game to 67 Games:

1. Create a game class that inherits from `BaseGame` (see `base_game.py`)
2. Create a controller for the game (see `counting_game_controller.py` for example)
3. Add the game to `game_launcher.py` menu

Example:
```python
def launch_my_game(model_type="mediapipe"):
    controller = MyGameController(model_type=model_type)
    controller.run()

# In main() function:
menu.add_game(
    "My Game",
    "Description of my game",
    lambda: launch_my_game(model_type=args.model)
)
```

## Troubleshooting

- **Hand detection not working**: Make sure MediaPipe is installed correctly or YOLO models are downloaded
- **Menu not showing**: Check that pygame is installed: `pip install pygame`
- **Games not launching**: Check console for error messages
