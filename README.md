# Computer Vision Projects with Hand Tracking

A collection of interactive computer vision applications using OpenCV and MediaPipe for hand gesture recognition and control.

## 🎯 Projects Overview

### 1. 🎮 NinjaFruit - Hand Gesture Fruit Slicing Game

A fun arcade-style game where you slice falling fruits using hand gestures. Features multiple fruit types, bombs to avoid, particle effects, and score tracking.

### 2. 🔊 VolumeHandControl - Gesture-Based Volume Control

Control your system volume by pinching your thumb and index finger. Real-time volume adjustment with visual feedback.

### 3. 🎨 AirPaint - Virtual Drawing Application

Create digital artwork using hand gestures. Features multiple colors, brush sizes, eraser, and smooth drawing with gesture controls.

## 🛠️ Prerequisites

### Required Python Packages

```bash
pip install opencv-python
pip install mediapipe
pip install numpy
pip install comtypes
pip install pycaw
```

### System Requirements

- **OS**: Windows 10/11 (for VolumeHandControl), macOS/Linux (other projects)
- **Camera**: Webcam for hand tracking
- **Python**: 3.7 or higher

## 📦 Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ensure your webcam** is connected and accessible

## 🎮 Project Details

### NinjaFruit Game

**File**: `NinjaFruit.py`

**How to Play**:

- Show your hand to the camera
- Use your index finger to slice falling fruits
- Avoid black bombs (they reduce lives)
- Different fruits give different points:
  - 🍎 Apple: 10 points
  - 🍊 Orange: 15 points
  - 🍌 Banana: 20 points
  - 🍓 Strawberry: 25 points
  - 🍉 Watermelon: 30 points

**Features**:

- Multiple difficulty levels
- Particle effects for sliced fruits
- High score tracking
- Lives system
- Combo multipliers
- Smooth hand tracking

**Controls**:

- **Index finger up**: Slice fruits
- **All fingers up**: Clear screen (in menu)
- **ESC**: Exit game

### VolumeHandControl

**File**: `VolumeHandControl.py`

**How to Use**:

- Show your hand to the camera
- Pinch your thumb and index finger together
- Move them apart to increase volume
- Bring them closer to decrease volume

**Features**:

- Real-time volume control
- Visual volume bar
- Percentage display
- Smooth gesture recognition
- System-level volume control

**Controls**:

- **Thumb + Index finger distance**: Controls volume
- **ESC**: Exit application

### AirPaint

**File**: `AirPaint.py`

**How to Use**:

- Show your hand to the camera
- Use different finger gestures for different tools

**Gesture Controls**:

- **Index finger only**: Draw mode
- **Index + Middle finger**: Selection mode (no drawing)
- **Thumb + Index finger**: Adjust brush thickness
- **Index + Middle + Ring finger**: Change colors
- **Index + Pinky finger**: Eraser mode
- **All fingers up**: Clear canvas

**Features**:

- 6 different colors (Magenta, Red, Green, Blue, Yellow, Cyan)
- Adjustable brush thickness (5-50 pixels)
- Smooth drawing with interpolation
- Eraser tool
- Clear canvas function
- Visual color palette
- Real-time thickness control

**Color Palette**:

- Click on color squares in the header to change colors
- Click "ERASE" button for eraser mode
- Click "CLEAR" button to clear canvas

## 🔧 Core Module

### HandTrackingModule

**File**: `HandTrackingModule.py`

This is the core hand tracking module used by all projects. It provides:

- **Hand Detection**: Real-time hand landmark detection
- **Finger Tracking**: Individual finger position tracking
- **Gesture Recognition**: Finger up/down state detection
- **Distance Calculation**: Euclidean distance between points

**Key Methods**:

- `findHands(img, draw=True)`: Detect and draw hand landmarks
- `findPosition(img, handNo=0)`: Get landmark coordinates
- `getFingers(img, handNo=0)`: Detect finger states [Thumb, Index, Middle, Ring, Pinky]
- `distance(point1, point2)`: Calculate distance between points

## 🚀 Running the Projects

### Quick Start

```bash
# Run NinjaFruit game
python NinjaFruit.py

# Run VolumeHandControl
python VolumeHandControl.py

# Run AirPaint
python AirPaint.py

# Test hand tracking module
python HandTrackingModule.py
```

### Tips for Best Performance

1. **Good Lighting**: Ensure your hand is well-lit
2. **Clear Background**: Avoid cluttered backgrounds
3. **Hand Position**: Keep your hand clearly visible to the camera
4. **Distance**: Maintain 20-60cm distance from camera
5. **Stable Camera**: Keep the camera steady

## 🎯 Troubleshooting

### Common Issues

**Camera not detected**:

- Check if webcam is connected and not in use by other applications
- Try different camera indices (change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`)

**Poor hand detection**:

- Improve lighting conditions
- Ensure hand is clearly visible
- Check camera focus

**Volume control not working** (VolumeHandControl):

- Ensure you're on Windows
- Check if `pycaw` and `comtypes` are installed
- Run as administrator if needed

**Performance issues**:

- Close other applications using the camera
- Reduce camera resolution if needed
- Check system resources

## 📁 Project Structure

```
opencv/
├── README.md                 # This file
├── HandTrackingModule.py     # Core hand tracking module
├── NinjaFruit.py            # Fruit slicing game
├── VolumeHandControl.py     # Volume control application
└── AirPaint.py             # Virtual drawing application
```

## 🎨 Customization

### Adjusting Detection Sensitivity

In each project, you can modify the `detectionCon` parameter:

```python
detector = htm.handDetector(detectionCon=0.75)  # 0.5-0.9 range
```

### Changing Camera Resolution

Modify the `wCam` and `hCam` variables:

```python
wCam, hCam = 1280, 720  # Higher resolution
wCam, hCam = 640, 480   # Lower resolution (better performance)
```

### Adding New Gestures

Extend the `getFingers()` method in `HandTrackingModule.py` to recognize new finger patterns.

## 🤝 Contributing

Feel free to contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **MediaPipe**: Hand tracking technology by Google
- **OpenCV**: Computer vision library
- **PyCAW**: Windows audio control library

---

**Enjoy exploring these interactive computer vision projects! 🚀**
