import cv2
import mediapipe as mp
import numpy as np
import time
import logging
from collections import deque

class MalpracticeDetection:
    def __init__(self):
        # Initialize MediaPipe FaceMesh with iris tracking
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=2,  # Allow detection of multiple faces for alerts
            refine_landmarks=True,  # Enable iris tracking
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Iris landmark indexes
        self.LEFT_IRIS_INDEXES = list(range(474, 478))
        self.RIGHT_IRIS_INDEXES = list(range(469, 473))

        # Eye corner landmark indexes for gaze calculation
        self.LEFT_EYE_CORNERS = [33, 133]  # Left eye: left corner, right corner
        self.RIGHT_EYE_CORNERS = [362, 263]  # Right eye: left corner, right corner

        # Kalman filters for smoothing iris centers
        self.left_kalman = self._init_kalman_filter()
        self.right_kalman = self._init_kalman_filter()

        # Alert thresholds and timers
        self.look_away_threshold = 3.0  # seconds
        self.look_away_timer = 0
        self.last_face_detected_time = time.time()

        # Calibration variables
        self.gaze_thresholds = {'left': 0.35, 'right': 0.35}  # Default thresholds
        self.calibrated = False

        # Logging setup
        logging.basicConfig(filename='malpractice_log.txt', level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')

        # Frame buffer for smoothing
        self.frame_buffer_size = 5
        self.left_gaze_buffer = deque(maxlen=self.frame_buffer_size)
        self.right_gaze_buffer = deque(maxlen=self.frame_buffer_size)

    def _init_kalman_filter(self):
        """Initialize a simple Kalman filter for smoothing."""
        kf = cv2.KalmanFilter(4, 2)
        kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        kf.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) * 0.03
        kf.measurementNoiseCov = np.array([[1, 0], [0, 1]], np.float32) * 0.1
        return kf

    def calibrate_gaze(self, frame):
        """Calibration step to set personalized gaze thresholds."""
        print("Calibration: Look directly at the screen for 5 seconds...")
        start_time = time.time()
        left_ratios = []
        right_ratios = []

        while time.time() - start_time < 5:
            ret, cal_frame = frame.copy() if frame is not None else (False, None)
            if not ret:
                continue

            h, w, _ = cal_frame.shape
            rgb = cv2.cvtColor(cal_frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                mesh_points = face_landmarks.landmark

                left_ratio = self._calculate_gaze_ratio(mesh_points, self.LEFT_EYE_CORNERS, self.LEFT_IRIS_INDEXES, w, h)
                right_ratio = self._calculate_gaze_ratio(mesh_points, self.RIGHT_EYE_CORNERS, self.RIGHT_IRIS_INDEXES, w, h)

                if left_ratio and right_ratio:
                    left_ratios.append(left_ratio)
                    right_ratios.append(right_ratio)

            cv2.putText(cal_frame, "Calibrating... Look at screen", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Calibration", cal_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if left_ratios and right_ratios:
            self.gaze_thresholds['left'] = np.mean(left_ratios) - 0.1  # Slightly more restrictive
            self.gaze_thresholds['right'] = np.mean(right_ratios) - 0.1
            self.calibrated = True
            print(f"Calibration complete. Thresholds: Left={self.gaze_thresholds['left']:.3f}, Right={self.gaze_thresholds['right']:.3f}")
        else:
            print("Calibration failed. Using default thresholds.")

    def _calculate_gaze_ratio(self, mesh_points, eye_corners, iris_indexes, w, h):
        """Calculate horizontal gaze ratio for one eye."""
        try:
            # Get eye corner positions
            eye_left = np.array([mesh_points[eye_corners[0]].x * w, mesh_points[eye_corners[0]].y * h])
            eye_right = np.array([mesh_points[eye_corners[1]].x * w, mesh_points[eye_corners[1]].y * h])

            # Get iris center
            iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in iris_indexes])
            iris_center = np.mean(iris_points, axis=0)

            # Calculate distances
            eye_width = np.linalg.norm(eye_right - eye_left)
            iris_to_left = np.linalg.norm(iris_center - eye_left)
            iris_to_right = np.linalg.norm(iris_center - eye_right)

            # Gaze ratio: closer to 0 means looking left, closer to 1 means looking right
            if eye_width > 0:
                gaze_ratio = iris_to_left / (iris_to_left + iris_to_right)
                return gaze_ratio
        except:
            return None

    def _smooth_iris_center(self, center, kalman_filter):
        """Apply Kalman filtering to smooth iris center coordinates."""
        measurement = np.array([[np.float32(center[0])], [np.float32(center[1])]])
        kalman_filter.correct(measurement)
        prediction = kalman_filter.predict()
        return (int(prediction[0]), int(prediction[1]))

    def _is_looking_at_screen(self, left_ratio, right_ratio):
        """Determine if student is looking at the screen based on gaze ratios."""
        if left_ratio is None or right_ratio is None:
            return False

        # Student is looking at screen if both eyes are within thresholds
        left_on_screen = abs(left_ratio - 0.5) < self.gaze_thresholds['left']
        right_on_screen = abs(right_ratio - 0.5) < self.gaze_thresholds['right']

        return left_on_screen and right_on_screen

    def _draw_overlays(self, frame, face_landmarks, left_center, right_center, left_ratio, right_ratio, alerts):
        """Draw visual overlays on the frame."""
        h, w, _ = frame.shape
        mesh_points = face_landmarks.landmark

        # Draw iris centers
        if left_center:
            cv2.circle(frame, left_center, 3, (0, 255, 0), -1)
            cv2.line(frame, (left_center[0] - 10, left_center[1]), (left_center[0] + 10, left_center[1]), (0, 255, 0), 1)
            cv2.line(frame, (left_center[0], left_center[1] - 10), (left_center[0], left_center[1] + 10), (0, 255, 0), 1)

        if right_center:
            cv2.circle(frame, right_center, 3, (0, 255, 0), -1)
            cv2.line(frame, (right_center[0] - 10, right_center[1]), (right_center[0] + 10, right_center[1]), (0, 255, 0), 1)
            cv2.line(frame, (right_center[0], right_center[1] - 10), (right_center[0], right_center[1] + 10), (0, 255, 0), 1)

        # Display gaze ratios
        if left_ratio is not None:
            cv2.putText(frame, f"Left Gaze: {left_ratio:.3f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        if right_ratio is not None:
            cv2.putText(frame, f"Right Gaze: {right_ratio:.3f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Display alerts
        y_offset = 90
        for alert in alerts:
            color = (0, 0, 255) if "ALERT" in alert else (0, 255, 255)
            cv2.putText(frame, alert, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30

        # Display calibration status
        if self.calibrated:
            cv2.putText(frame, "Calibrated", (w - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Not Calibrated", (w - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

    def _log_event(self, event_type, details=""):
        """Log suspicious events."""
        logging.info(f"{event_type}: {details}")
        print(f"[{time.strftime('%H:%M:%S')}] {event_type}: {details}")

    def run_detection(self):
        """Main detection loop."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return

        print("Malpractice Detection Started")
        print("Press 'c' to calibrate, 'q' to quit")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)  # Flip horizontally for mirror effect
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            alerts = []
            current_time = time.time()

            # Check for faces
            if not results.multi_face_landmarks:
                alerts.append("ALERT: No face detected!")
                self.look_away_timer = 0
                if current_time - self.last_face_detected_time > 5:
                    self._log_event("NO_FACE_DETECTED", "Face not detected for 5+ seconds")
                    self.last_face_detected_time = current_time
            elif len(results.multi_face_landmarks) > 1:
                alerts.append("ALERT: Multiple faces detected!")
                self._log_event("MULTIPLE_FACES", f"{len(results.multi_face_landmarks)} faces detected")
            else:
                self.last_face_detected_time = current_time

                # Process single face
                face_landmarks = results.multi_face_landmarks[0]
                mesh_points = face_landmarks.landmark

                # Calculate iris centers with smoothing
                left_iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in self.LEFT_IRIS_INDEXES])
                right_iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in self.RIGHT_IRIS_INDEXES])

                left_center_raw = np.mean(left_iris_points, axis=0).astype(int)
                right_center_raw = np.mean(right_iris_points, axis=0).astype(int)

                left_center = self._smooth_iris_center(left_center_raw, self.left_kalman)
                right_center = self._smooth_iris_center(right_center_raw, self.right_kalman)

                # Calculate gaze ratios
                left_ratio = self._calculate_gaze_ratio(mesh_points, self.LEFT_EYE_CORNERS, self.LEFT_IRIS_INDEXES, w, h)
                right_ratio = self._calculate_gaze_ratio(mesh_points, self.RIGHT_EYE_CORNERS, self.RIGHT_IRIS_INDEXES, w, h)

                # Add to buffers for smoothing
                if left_ratio is not None:
                    self.left_gaze_buffer.append(left_ratio)
                if right_ratio is not None:
                    self.right_gaze_buffer.append(right_ratio)

                # Use smoothed ratios
                smoothed_left = np.mean(self.left_gaze_buffer) if self.left_gaze_buffer else left_ratio
                smoothed_right = np.mean(self.right_gaze_buffer) if self.right_gaze_buffer else right_ratio

                # Check if looking at screen
                looking_at_screen = self._is_looking_at_screen(smoothed_left, smoothed_right)

                if not looking_at_screen:
                    self.look_away_timer += 1/30  # Assuming 30 FPS
                    if self.look_away_timer > self.look_away_threshold:
                        alerts.append(f"ALERT: Looking away for {self.look_away_timer:.1f}s!")
                        if int(self.look_away_timer) % 5 == 0:  # Log every 5 seconds
                            self._log_event("LOOKING_AWAY", f"Duration: {self.look_away_timer:.1f} seconds")
                else:
                    if self.look_away_timer > self.look_away_threshold:
                        self._log_event("RESUMED_ATTENTION", f"After {self.look_away_timer:.1f} seconds away")
                    self.look_away_timer = 0

                # Draw overlays
                self._draw_overlays(frame, face_landmarks, left_center, right_center, smoothed_left, smoothed_right, alerts)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c') and not self.calibrated:
                self.calibrate_gaze(frame)

            cv2.imshow("Malpractice Detection", frame)

        cap.release()
        cv2.destroyAllWindows()
        print("Detection stopped")

if __name__ == "__main__":
    detector = MalpracticeDetection()
    detector.run_detection()