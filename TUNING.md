# Hand Gesture Control Tuning Guide

This guide explains how to fine-tune the hand gesture sensitivity and responsiveness for your setup.

## Current Settings (Optimized for High Sensitivity)

The game is currently configured for **maximum sensitivity and responsiveness**:

### In `main.py` (Lines ~56-58):
```python
self.jump_threshold = 15          # Pixels hand must move up
self.frame_skip = 1               # Process every frame
self.jump_cooldown_frames = 5     # Cooldown between jumps
```

### In `hand_detector.py` (Lines ~26-27 for YOLO):
```python
self.confidence_threshold = 0.3   # YOLO detection confidence
```

### In `hand_detector.py` (Lines ~48-49 for MediaPipe):
```python
min_detection_confidence=0.3      # MediaPipe detection
min_tracking_confidence=0.3       # MediaPipe tracking
```

## Tuning Parameters

### 1. Jump Sensitivity (`jump_threshold`)

**Location**: `main.py` line ~56

Controls how many pixels your hand must move upward to trigger a jump.

| Value | Sensitivity | Description |
|-------|------------|-------------|
| 10-15 | **Very High** ✅ (Current) | Small hand movements trigger jumps |
| 20-30 | Medium | Moderate movements needed |
| 35-50 | Low | Large deliberate movements only |

**When to adjust:**
- **Too sensitive?** (Jumping too often) → Increase to 20-25
- **Not sensitive enough?** → Decrease to 10-12

```python
self.jump_threshold = 15  # Change this value
```

### 2. Frame Processing (`frame_skip`)

**Location**: `main.py` line ~57

Controls how often the camera is processed. Lower = more responsive but more CPU usage.

| Value | Responsiveness | CPU Usage |
|-------|----------------|-----------|
| 1 | **Maximum** ✅ (Current) | High |
| 2 | Good | Medium |
| 3-4 | Acceptable | Low |

**When to adjust:**
- **Game lagging?** → Increase to 2 or 3
- **Want faster response?** → Keep at 1

```python
self.frame_skip = 1  # Change this value
```

### 3. Jump Cooldown (`jump_cooldown_frames`)

**Location**: `main.py` line ~59

Prevents rapid-fire jumps. Time between jumps = cooldown ÷ 60 seconds (at 60 FPS).

| Value | Cooldown Time | Description |
|-------|---------------|-------------|
| 3-5 | 0.05-0.08s | **Fast** ✅ (Current) |
| 8-10 | 0.13-0.17s | Moderate |
| 15-20 | 0.25-0.33s | Slow |

**When to adjust:**
- **Accidentally double-jumping?** → Increase to 8-10
- **Want more control?** → Decrease to 3

```python
self.jump_cooldown_frames = 5  # Change this value
```

### 4. Detection Confidence (MediaPipe)

**Location**: `hand_detector.py` lines ~48-49

How confident the model must be to detect a hand.

| Value | Detection | Stability |
|-------|-----------|-----------|
| 0.3 | **Easy** ✅ (Current) | May have false positives |
| 0.5 | Balanced | Good |
| 0.7 | Strict | Very stable, may miss hands |

**When to adjust:**
- **Detecting non-hands?** → Increase to 0.5-0.6
- **Not detecting hands?** → Decrease to 0.2-0.3

```python
min_detection_confidence=0.3,  # Change these values
min_tracking_confidence=0.3
```

### 5. YOLO Confidence Threshold

**Location**: `hand_detector.py` line ~27

Same as above but for YOLO models.

```python
self.confidence_threshold = 0.3  # Change this value
```

## Recommended Presets

### 🎯 Preset 1: Maximum Sensitivity (Current - Best for Games)
```python
# main.py
self.jump_threshold = 15
self.frame_skip = 1
self.jump_cooldown_frames = 5

# hand_detector.py (MediaPipe)
min_detection_confidence=0.3
min_tracking_confidence=0.3
```

### 🎮 Preset 2: Balanced (Good for Most Users)
```python
# main.py
self.jump_threshold = 20
self.frame_skip = 2
self.jump_cooldown_frames = 8

# hand_detector.py (MediaPipe)
min_detection_confidence=0.4
min_tracking_confidence=0.4
```

### 🎯 Preset 3: Precise Control (For Pros)
```python
# main.py
self.jump_threshold = 25
self.frame_skip = 1
self.jump_cooldown_frames = 3

# hand_detector.py (MediaPipe)
min_detection_confidence=0.5
min_tracking_confidence=0.5
```

### 💻 Preset 4: Low-End PC (Performance Mode)
```python
# main.py
self.jump_threshold = 20
self.frame_skip = 3
self.jump_cooldown_frames = 10

# hand_detector.py (MediaPipe)
min_detection_confidence=0.5
min_tracking_confidence=0.5
```

## Quick Tuning Workflow

1. **Start with current settings** (Preset 1)
2. **Test the game** for 2-3 minutes
3. **Identify the issue:**
   - Jumping too much? → Increase `jump_threshold`
   - Not jumping enough? → Decrease `jump_threshold`
   - Game lagging? → Increase `frame_skip`
   - Double jumps? → Increase `jump_cooldown_frames`
   - Hand not detected? → Decrease confidence thresholds
4. **Make ONE change at a time**
5. **Test again**
6. **Repeat until satisfied**

## Advanced: Per-Hand Sensitivity

If you want different sensitivity for left vs right hand, you can modify the `process_hand_gesture()` method in `main.py` to use different thresholds based on `handedness`:

```python
# In process_hand_gesture() method
threshold = 15 if handedness == 'Left' else 20  # Left hand more sensitive
if last_y - center_y > threshold:
    should_jump = True
```

## Testing Your Changes

After making changes:

1. Save the file
2. Restart the game: `python main.py`
3. Test with your hand gestures
4. Check the webcam feed for detection accuracy
5. Play a few rounds to verify behavior

## Reverting to Defaults

If you want to go back to less sensitive settings (original):

```python
# main.py - Original conservative settings
self.jump_threshold = 30
self.frame_skip = 2
self.jump_cooldown_frames = 0  # No cooldown

# hand_detector.py
self.confidence_threshold = 0.5  # YOLO
min_detection_confidence=0.5     # MediaPipe
min_tracking_confidence=0.5      # MediaPipe
```

---

**Pro Tip**: Keep a backup copy of your working configuration before experimenting!

Enjoy tuning your perfect hand gesture controls! 🎮👋

