# Online Exam Malpractice Detection System

A real-time computer vision system for detecting suspicious behavior during online exams using webcam feed analysis.

## Features

- **Real-time Face Detection**: Uses MediaPipe FaceMesh with iris refinement for accurate face tracking
- **Iris Detection & Tracking**: Extracts and tracks iris landmark points with Kalman filtering for smooth detection
- **Gaze Direction Estimation**: Calculates horizontal gaze ratios to determine if the student is looking at the screen
- **Suspicious Behavior Alerts**:
  - No face detected
  - Multiple faces detected
  - Student looking away from screen for extended periods
- **Visual Overlays**:
  - Iris center markers
  - Real-time gaze ratio display
  - Alert messages on video feed
- **Calibration System**: Personalized gaze thresholds for accurate detection
- **Logging System**: Records timestamps of suspicious events to file
- **Modular Design**: Easy to extend with head pose estimation, blink detection, etc.

## Requirements

- Python 3.7+
- Webcam
- Dependencies: opencv-python, mediapipe, numpy

## Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the malpractice detection system:

```bash
python malpractice_detection.py
```

### Controls

- **'c'**: Start calibration (look at screen for 5 seconds)
- **'q'**: Quit the application

### Calibration

For best results, calibrate the system before starting the exam:
1. Run the script
2. Press 'c' when prompted
3. Look directly at the screen for 5 seconds
4. The system will automatically set personalized gaze thresholds

## How It Works

1. **Face Detection**: MediaPipe FaceMesh detects facial landmarks including refined iris points
2. **Iris Tracking**: Extracts 4 landmark points per iris and calculates center coordinates
3. **Gaze Estimation**: Computes horizontal gaze ratio based on iris position relative to eye corners
4. **Smoothing**: Applies Kalman filtering to reduce jitter in iris center detection
5. **Alert Logic**:
   - Monitors for face presence
   - Tracks gaze direction against calibrated thresholds
   - Times look-away periods
6. **Visualization**: Overlays detection results and alerts on the video feed

## Configuration

Key parameters can be adjusted in the `MalpracticeDetection` class:

- `look_away_threshold`: Seconds before triggering look-away alert (default: 3.0)
- `gaze_thresholds`: Default gaze ratio thresholds (adjusted during calibration)
- `frame_buffer_size`: Number of frames for gaze ratio smoothing (default: 5)

## Output

- **Video Feed**: Real-time display with overlays and alerts
- **Console Output**: Real-time alert messages
- **Log File**: `malpractice_log.txt` with timestamped events

## Future Enhancements

- Head pose estimation
- Blink detection
- Facial expression analysis
- Multiple camera support
- Integration with exam platforms
- Advanced machine learning models

## Technical Details

- **Face Detection**: MediaPipe FaceMesh with 478 landmarks (including iris)
- **Iris Landmarks**: Left eye (474-477), Right eye (469-472)
- **Gaze Calculation**: Horizontal ratio based on eye corner distances
- **Smoothing**: Kalman filter for coordinate stabilization
- **Performance**: Optimized for real-time processing at 30+ FPS

## License

See LICENSE file for details.