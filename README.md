# Hand Gesture Control

A production-ready application for controlling your computer with hand gestures using MediaPipe and OpenCV.

## Features
- **Mouse Control**: Move, Click, Double Click, Drag, Scroll.
- **Volume & Brightness**: Control using finger pinches.
- **Media Controls**: Play/Pause, Next/Prev, Mute.
- **Presentation Mode**: Next/Prev slide, Zoom.
- **Drawing Mode**: Draw on screen using your index finger.

## Installation

1. Clone or download the repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```bash
python main.py
```

### Gestures:
- **Mouse Move**: Point index finger up, keep other fingers down.
- **Left Click**: Pinch index and middle fingers together.
- **Right Click**: Pinch thumb and middle fingers together.
- **Volume**: In mouse mode, pinch thumb and index finger together to control volume based on distance.

## Building Executable

To build a standalone `.exe` for Windows:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run the build command:
   ```bash
   python -m PyInstaller --noconfirm --onedir --windowed --add-data "config.json;." main.py
   ```
