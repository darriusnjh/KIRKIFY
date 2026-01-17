# 🎮 Alternating Hands Mode

## Overview

The game now requires you to **alternate between left and right hands** to make the bird jump! This creates a more challenging and engaging gameplay experience.

## How It Works

### The Pattern
```
Jump 1: 👈 Wave LEFT hand UP
Jump 2: 👉 Wave RIGHT hand UP  
Jump 3: 👈 Wave LEFT hand UP
Jump 4: 👉 Wave RIGHT hand UP
...and so on!
```

### Rules
1. ✅ First jump can be with **either hand**
2. ✅ After that, you **must alternate** between left and right
3. ❌ Waving the **same hand twice** in a row will **NOT** register the second jump
4. ✅ Both hands can be visible, but only the **correct hand's gesture** will trigger a jump

## Visual Feedback

### On-Screen Indicators

The game shows you which hand to use next:

#### Top of Screen (BIG text):
- **"Wave Either Hand!"** (Yellow) - First jump, use any hand
- **"Wave LEFT Hand! 👈"** (Blue) - Left hand's turn
- **"Wave RIGHT Hand! 👉"** (Red) - Right hand's turn

#### Below That:
- Shows detected hands with confidence percentage
- **Active hand** (the one that should jump) is highlighted in **bright yellow** with **>>> arrows <<<**

### Example Display
```
Wave RIGHT Hand! 👉         ← BIG indicator at top

Left Hand: 94%              ← Detected but not active
>>> Right Hand: 98% <<<     ← ACTIVE! This one should jump
```

## Playing Tips

### 1. Keep Both Hands Visible
- Position yourself so the camera can see both hands
- Keep hands spread apart for better detection
- Good lighting helps!

### 2. Clear Gestures
- Make **distinct upward movements** with each hand
- Don't wave both hands at the same time
- Wait a moment between left and right gestures

### 3. Watch the Indicator
- Always check which hand is shown at the top
- The **color** tells you which hand to use:
  - 🔵 **Blue** = Left hand
  - 🔴 **Red** = Right hand
  - 🟡 **Yellow** = Either hand (first jump only)

### 4. Rhythm
Establish a rhythm: 
```
LEFT → pause → RIGHT → pause → LEFT → pause → RIGHT
```

## Technical Details

### Detection System
- Uses **MediaPipe** for left/right hand classification
- Tracks hand positions independently
- Registers jump when hand moves up **80+ pixels**
- **1 frame** cooldown between jumps (~0.016s)

### Alternating Logic
```python
if current_hand_gesture AND current_hand != last_jump_hand:
    jump()
    last_jump_hand = current_hand
else:
    ignore_gesture()  # Same hand as last time
```

## Requirements

### ⚠️ MediaPipe is REQUIRED
The alternating hands feature **only works with MediaPipe** because:
- YOLO models cannot distinguish between left and right hands
- MediaPipe provides the `handedness` classification

### Setup
```bash
# Make sure MediaPipe is installed
pip install mediapipe==0.10.9

# Run the game (MediaPipe is default)
python main.py
```

### Check Your Setup
```bash
# Verify MediaPipe is working
python diagnose_setup.py

# Should show:
# [OK] MediaPipe installed
# [OK] MediaPipe Hands initialized successfully
```

## Gameplay Strategies

### Beginner Strategy
1. Start slow - get used to the alternating pattern
2. Watch the on-screen indicator constantly
3. Make exaggerated hand movements
4. Don't rush - timing > speed

### Advanced Strategy
1. Develop muscle memory for L→R→L→R rhythm
2. Use peripheral vision to watch indicator
3. Make smaller, quicker gestures
4. Anticipate pipe gaps and alternate accordingly

### Pro Strategy
1. Pre-plan your hand sequence based on pipe patterns
2. Sync alternating pattern with game obstacles
3. Minimal hand movements for speed
4. Eyes on the bird, not the indicator

## Common Issues & Solutions

### Issue: "Same hand keeps triggering"
**Solution**: 
- Make sure you're alternating hands
- Check the indicator to see which hand should go next
- Clear hand gesture (move hand up more)

### Issue: "Jumps not registering"
**Solution**:
- Increase hand movement (currently needs 80px)
- Ensure proper lighting
- Make sure both hands are visible
- Check if you're using the correct hand (watch indicator)

### Issue: "Can't tell which hand to use"
**Solution**:
- Look at the BIG text at the top of the screen
- Blue = Left, Red = Right, Yellow = Either
- The current hand is marked with >>> arrows <<<

### Issue: "MediaPipe not detecting left/right"
**Solution**:
```bash
# Reinstall MediaPipe
pip uninstall mediapipe -y
pip install mediapipe==0.10.9

# Verify
python test_hand_detector.py --mode webcam
```

## Keyboard Override

Don't worry! You can still use **SPACE bar** to jump if:
- Hand detection isn't working well
- You want to practice
- You're too tired to alternate hands 😅

The keyboard doesn't require alternating - it works normally!

## Adjusting Difficulty

You can modify the alternating requirement by editing `main.py`:

### Make it easier (allow same hand multiple times):
Comment out the alternating check:
```python
# if self.last_jump_hand is None or self.last_jump_hand != handedness:
if True:  # Allow any hand
    should_jump = True
```

### Make it harder (require perfect timing):
Increase the cooldown:
```python
self.jump_cooldown_frames = 10  # Longer cooldown between jumps
```

## Fun Variations to Try

1. **Speed Challenge**: How fast can you alternate?
2. **One Hand Only**: Use only left or right (very hard!)
3. **Pattern Mode**: L→L→R→R→L→L→R→R (modify the code)
4. **No Indicator**: Hide the on-screen help (for pros)

---

**Have fun and get those hands moving!** 👋👋

The alternating hands mechanic adds a physical challenge that makes the game more engaging and helps develop coordination!

