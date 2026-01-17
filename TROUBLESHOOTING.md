# Troubleshooting Guide

## Common Issues and Solutions

### 1. Hand Detection Not Working After Being Still

**Problem**: The model struggles to detect hand waving motion after the hand has not moved for a while.

**Root Cause**: Position tracking becomes "stale" - when a hand is stationary, the tracked position stays at that location. When you try to move it again, the system compares against a very recent position, making it hard to detect the upward movement.

**Solution Implemented**: ✅ Fixed!

The system now:
1. **Tracks stillness**: Monitors if hand movement is < 5 pixels per frame
2. **Counts still frames**: Increments a counter when hand is still
3. **Auto-resets**: After 30 frames (~0.5 seconds) of being still, position tracking resets
4. **Fresh start**: Next movement is detected as if it's a new hand gesture

**How it works**:
```python
# If hand hasn't moved for 0.5 seconds
if frames_still >= 30:
    # Reset tracking - treat next movement as fresh gesture
    reset_position_tracking()
```

**What this means for gameplay**:
- Hold your hand still to "reset" the tracking
- After 0.5 seconds of stillness, the next wave will be detected properly
- No more "stuck" hand detection!

---

### 2. Hands Not Detected at All

**Symptoms**: "No hands detected" message appears constantly

**Possible Causes & Solutions**:

#### A. MediaPipe Not Installed
```bash
# Check installation
python diagnose_setup.py

# If not installed, install it
pip install mediapipe==0.10.9
```

#### B. Poor Lighting
- Ensure room is well-lit
- Avoid backlighting (don't sit in front of a bright window)
- Face a light source if possible

#### C. Camera Not Working
```bash
# Test camera directly
python test_hand_detector.py --mode webcam
```

#### D. Hands Not in Frame
- Keep hands visible to camera
- Don't move hands too close or too far
- Optimal distance: 1-2 feet from camera

#### E. Background Too Cluttered
- Try a cleaner background
- Avoid backgrounds with skin-tone colors
- Spread fingers apart for better detection

---

### 3. Wrong Hand Detected (Left/Right Confusion)

**Symptoms**: Game says to use left hand but detects right, or vice versa

**Cause**: MediaPipe's handedness is from the camera's perspective (mirrored)

**Solution**: The code already flips the frame for mirror effect. If still having issues:

```python
# In main.py, verify this line exists:
frame = cv2.flip(frame, 1)  # Horizontal flip for mirror effect
```

**Note**: The handedness detection is relative to YOU, not the camera. Your left hand should be detected as "Left".

---

### 4. Too Many False Jumps

**Symptoms**: Bird jumps when you don't want it to

**Solutions**:

#### A. Increase Jump Threshold
```python
# In main.py, line ~57
self.jump_threshold = 30  # Increase to 40 or 50
```

#### B. Add Jump Cooldown
```python
# In main.py, line ~60
self.jump_cooldown_frames = 5  # Add 5-10 frame cooldown
```

#### C. Reduce Detection Sensitivity
```python
# In hand_detector.py, line ~56
min_detection_confidence=0.5  # Increase from 0.3
```

---

### 5. Not Enough Jumps (Too Strict)

**Symptoms**: Hard to make the bird jump

**Solutions**:

#### A. Decrease Jump Threshold
```python
# In main.py, line ~57
self.jump_threshold = 20  # Decrease from 30
```

#### B. Increase Detection Sensitivity
```python
# In hand_detector.py, line ~56
min_detection_confidence=0.2  # Decrease from 0.3
```

#### C. Make Bigger Gestures
- Move hand further up (>30 pixels)
- Make quick, deliberate movements
- Ensure good lighting

---

### 6. Alternating Not Working

**Symptoms**: Same hand gesture works multiple times in a row

**Cause**: Likely using YOLO model instead of MediaPipe

**Solution**:
```bash
# Make sure you're using MediaPipe (default)
python main.py

# Or explicitly
python main.py -m mediapipe

# Check if MediaPipe is working
python diagnose_setup.py
```

**YOLO models cannot detect left/right**, so alternating mode requires MediaPipe!

---

### 7. Game is Laggy

**Symptoms**: Low FPS, stuttering, slow response

**Solutions**:

#### A. Reduce Frame Processing
```python
# In main.py, line ~58
self.frame_skip = 2  # Process every 2nd frame instead of every frame
```

#### B. Close Other Applications
- Close browser tabs
- Close other programs
- Free up RAM and CPU

#### C. Lower Webcam Resolution
```python
# In main.py, after cv2.VideoCapture(0)
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

---

### 8. MediaPipe Installation Issues

**Symptoms**: AttributeError: module 'mediapipe' has no attribute 'solutions'

**Solution**:
```bash
# Complete reinstall
pip uninstall mediapipe -y
pip cache purge
pip install mediapipe==0.10.9

# Verify
python -c "import mediapipe as mp; print(mp.__version__); print(hasattr(mp, 'solutions'))"
```

**Expected output**:
```
0.10.9
True
```

---

### 9. Hands Detected But No Jumps

**Possible Causes**:

#### A. Not Moving Enough
- Need to move hand up at least 30 pixels
- Make bigger, more deliberate gestures

#### B. Wrong Hand (Alternating Mode)
- Check the on-screen indicator
- Use the hand shown in BLUE (left) or RED (right)

#### C. Position Tracking Issue
- Hold hand still for 1 second to reset tracking
- Then make a fresh upward gesture

---

### 10. Webcam Feed Not Showing

**Symptoms**: No camera preview in bottom-right corner

**Check**:
```python
# In game.py, verify webcam display code exists
if self.webcam_surface:
    scaled_surface = pygame.transform.scale(...)
    self.screen.blit(scaled_surface, ...)
```

**Possible Causes**:
- Webcam not initialized
- Another app using the camera
- Camera permission denied

---

## Debug Mode

Want to see what's happening? Add debug prints:

```python
# In main.py, in process_hand_gesture():
print(f"Hand: {handedness}, Y: {center_y}, Last Y: {last_y}, Still: {frames_still}")
```

This will print hand tracking info to the console.

---

## Performance Tips

### For Best Experience:
1. **Good lighting** - Bright, even lighting
2. **Clean background** - Solid color, not cluttered
3. **Webcam position** - Eye level, stable mount
4. **Hand visibility** - Keep both hands in frame
5. **Stillness reset** - Hold still briefly between rapid gestures
6. **Make it obvious** - Big, clear upward movements

### Optimal Setup:
- **Distance**: 1-2 feet from camera
- **Lighting**: Front-lit (light source facing you)
- **Background**: Solid wall, not busy patterns
- **Camera**: 720p or better, 30fps minimum
- **Position**: Camera centered, both hands visible

---

## Still Having Issues?

### Run Full Diagnostics:
```bash
python diagnose_setup.py
```

This checks:
- ✅ OpenCV installation
- ✅ Camera access
- ✅ NumPy installation
- ✅ MediaPipe installation
- ✅ MediaPipe Hands functionality
- ✅ YOLO models (if applicable)

### Test Hand Detection Alone:
```bash
python test_hand_detector.py --mode webcam
```

This lets you test hand detection without the game complexity.

### Check Your Settings:
See `TUNING.md` for all adjustable parameters and their effects.

---

## Getting Help

If none of these solutions work:

1. Run diagnostics: `python diagnose_setup.py`
2. Test hand detection: `python test_hand_detector.py --mode webcam`
3. Check your Python version: `python --version` (should be 3.8+)
4. Check your OS: The code works on Windows, Mac, and Linux
5. Verify camera works in other apps (Zoom, Skype, etc.)

**Common Environment Issues**:
- Virtual environment not activated
- Wrong Python interpreter
- Conflicting package versions
- Antivirus blocking camera access

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Hand stuck after being still | ✅ Already fixed! Wait 0.5s |
| Too sensitive | Increase `jump_threshold` to 40-50 |
| Not sensitive enough | Decrease `jump_threshold` to 15-20 |
| Laggy | Increase `frame_skip` to 2-3 |
| Wrong left/right | Check camera is mirrored (flip) |
| No detection | Check lighting and distance |
| MediaPipe error | Reinstall: `pip install mediapipe==0.10.9` |

---

**Remember**: The game works best with **good lighting**, **clear background**, and **both hands visible**!

Enjoy playing! 🎮👋

