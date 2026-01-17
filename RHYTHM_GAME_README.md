# 🎵 Rhythm Hand Game

A rhythm game controlled by your **left and right hand gestures**!

## 🎮 How to Play

### Start the Game
```bash
python rhythm_main.py
```

### Game Objective
- **Blue notes** fall in the left lane → Wave **LEFT hand 👈**
- **Red notes** fall in the right lane → Wave **RIGHT hand 👉**
- Hit notes at the **YELLOW line** for maximum points!

### Timing System

| Timing | Points | Window |
|--------|--------|--------|
| **PERFECT** 🌟 | 100 | ±20 pixels |
| **GOOD** ✅ | 50 | ±40 pixels |
| **OK** 👌 | 25 | ±60 pixels |
| **MISS** ❌ | 0 | Too late |

## 🎯 Scoring

- **Combo System**: Chain hits together for higher combos!
- **Accuracy Tracking**: Perfect hits give the best score
- **Total: 50 Notes** to complete the game

### Score Breakdown
```
Perfect Hit: 100 points
Good Hit: 50 points
OK Hit: 25 points
Miss: 0 points (breaks combo!)
```

## 🕹️ Controls

### Hand Gestures (Default)
- 👈 **Wave LEFT hand UP** → Hit left lane (blue notes)
- 👉 **Wave RIGHT hand UP** → Hit right lane (red notes)

### Keyboard (Testing/Fallback)
- **A key** → Left hand gesture
- **L key** → Right hand gesture
- **R key** → Restart after game over
- **ESC** → Quit game

## 🚀 Features

### ✨ Hand Gesture Recognition
- Uses **MediaPipe** for accurate left/right hand detection
- Automatic hand correction (ensures 1 left + 1 right max)
- **Live webcam feed** in bottom-right corner showing:
  - Hand detection bounding boxes
  - Hand landmarks (finger joints)
  - Color-coded: Blue (left) / Red (right)
- Real-time hand tracking display
- Works with the same system as Flappy Bird!

### 🎵 Rhythm Mechanics
- Notes spawn at regular intervals
- Two lanes (left and right)
- Visual hit zone indicator
- Immediate feedback (PERFECT/GOOD/OK/MISS)
- Combo counter

### 📊 Statistics
- Score tracking
- Combo counter (current and max)
- Hit accuracy breakdown
- Perfect/Good/OK/Miss counts

## 🎨 Visual Indicators

### Color System
- 🔵 **Blue** = Left lane notes
- 🔴 **Red** = Right lane notes
- 🟡 **Yellow** = Hit zone line
- 🟢 **Green** = "GOOD" feedback
- 🟡 **Yellow** = "PERFECT" feedback

### On-Screen Display
- **Top Left**: Score and combo
- **Top Right**: Progress (notes spawned)
- **Bottom Right**: Webcam feed with hand detection boxes
  - Blue boxes = Left hand
  - Red boxes = Right hand
  - Shows hand landmarks in real-time
- **Middle Sides**: Hand detection status text
- **Center**: Hit feedback (PERFECT/GOOD/OK/MISS)

## ⚙️ Configuration

### Command Line Options
```bash
# Default (MediaPipe with hand control)
python rhythm_main.py

# Keyboard only
python rhythm_main.py --no-hand

# Use YOLO model (not recommended - can't detect L/R)
python rhythm_main.py -m prn
```

### Adjust Difficulty

Edit `rhythm_game.py` to change:

```python
# Easier (slower notes)
NOTE_SPEED = 3

# Harder (faster notes)
NOTE_SPEED = 7

# More notes
SPAWN_INTERVAL = 20  # More frequent spawning

# Longer game
self.max_notes = 100  # Double the notes
```

### Adjust Timing Windows

Make it more/less forgiving:

```python
# More forgiving
PERFECT_WINDOW = 30  # Was 20
GOOD_WINDOW = 50     # Was 40

# More challenging
PERFECT_WINDOW = 15  # Was 20
GOOD_WINDOW = 30     # Was 40
```

## 🎓 Tips for High Scores

1. **Watch the Notes** 👀
   - Keep your eyes on the falling notes
   - Anticipate which hand to use

2. **Timing is Key** ⏰
   - Hit notes right at the yellow line
   - Perfect timing = maximum points

3. **Maintain Combo** 🔥
   - Don't miss notes!
   - Combos multiply your effectiveness

4. **Good Lighting** 💡
   - Ensure camera can see both hands clearly
   - Avoid shadows and backlighting

5. **Consistent Gestures** 🎯
   - Make clear, upward hand movements
   - Don't wave too early or late

6. **Practice** 📈
   - Start with keyboard mode (A/L keys)
   - Switch to hand gestures once comfortable

## 🐛 Troubleshooting

### Hands Not Detected
```bash
# Make sure MediaPipe is installed
pip install mediapipe==0.10.9

# Test hand detection
python test_hand_detector.py --mode webcam
```

### Wrong Hand Detected
- System automatically corrects this!
- Leftmost hand = Left
- Rightmost hand = Right

### Notes Too Fast/Slow
Edit `NOTE_SPEED` in `rhythm_game.py`

### Game Too Hard/Easy
Adjust `SPAWN_INTERVAL` and timing windows

## 📁 Files

- **`rhythm_game.py`** - Core game logic
- **`rhythm_main.py`** - Hand gesture integration
- **`hand_detector.py`** - Shared hand detection
- **`RHYTHM_GAME_README.md`** - This file!

## 🎮 Comparison with Flappy Bird

| Feature | Flappy Bird | Rhythm Game |
|---------|-------------|-------------|
| Hand Detection | ✅ Same system | ✅ Same system |
| Gesture | Upward wave | Upward wave |
| Alternating Required? | Yes | No |
| Left/Right Matters? | Yes (alternating) | Yes (match lane) |
| Timing | Continuous | Precise |
| Difficulty | Avoidance | Timing |

## 🌟 Game Modes

### Current: Standard Mode
- 50 notes total
- Random left/right pattern
- Fixed speed

### Potential Additions (DIY)
1. **Pattern Mode**: Predefined L-R-L-R sequences
2. **Speed Up**: Notes get faster over time
3. **Multiplayer**: Two players, each controls one hand
4. **Song Mode**: Sync notes to actual music
5. **Challenge Mode**: Only perfect hits count

## 🎉 End Screen

After all 50 notes, you'll see:
- **Final Score**
- **Max Combo**
- **Accuracy Percentage**
- **Hit Breakdown** (Perfect/Good/OK/Miss)

Press **R** to play again!

## 🚀 Quick Start

```bash
# 1. Make sure dependencies are installed
pip install mediapipe pygame opencv-python

# 2. Run the game
python rhythm_main.py

# 3. Wave your hands when you see notes!
```

---

**Have fun and hit those perfect notes!** 🎵👋

*Challenge yourself to get 100% accuracy and max combo!*

