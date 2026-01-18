# 67 Games

A collection of interactive games controlled by hand gestures using your webcam. Experience gaming without a controller!

## 🎮 Included Games

1.  **Flappy 67**: A gesture-controlled twist on the classic. Flap your hands to guide the bird!
2.  **Rhythm Game**: Hit notes to the beat using left and right hand gestures.
3.  **Counting Game**: Test your speed by making alternating hand gestures as fast as you can in 30 seconds.

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed. It is recommended to use a virtual environment.

### Installation

1.  Clone the repository (if applicable)
2.  Install the dependencies:

```bash
pip install -r requirements.txt
```

### Running the Games

Launch the main menu to choose your game:

```bash
python game_launcher.py
```

### Controls

- **Hand Control**: Most games track your hand position or specific gestures via the webcam. Ensure you have good lighting and your hand is visible.
- **Keyboard Control**: You can disable hand tracking and use keyboard controls for testing.

## ⚙️ Advanced Options

You can launch specific games directly or configure settings via command-line arguments:

```bash
# Launch Flappy Bird directly
python game_launcher.py --game flappy

# Launch Rhythm Game directly
python game_launcher.py --game rhythm

# Launch Counting Game directly
python game_launcher.py --game counting

# Run without hand tracking (Keyboard mode)
python game_launcher.py --no-hand
```

## 🛠️ Technology Stack

- **Python**: Core logic
- **Pygame**: Game rendering and loop
- **OpenCV & MediaPipe**: Real-time computer vision and hand tracking
- **Numpy**: Mathematical operations
