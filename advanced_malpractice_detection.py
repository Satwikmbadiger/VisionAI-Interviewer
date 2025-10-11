import cv2
import mediapipe as mp
import numpy as np
import time
import logging
import threading
import queue
import os
from collections import deque
from scipy.spatial.distance import cosine
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    tf = None
    TENSORFLOW_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    PYGAME_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    pyaudio = None
    PYAUDIO_AVAILABLE = False

class FaceTracker:
    """Handles face detection, tracking, identity verification, and head pose estimation."""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=3,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Face embeddings for identity verification
        self.reference_embedding = None
        self.embedding_history = deque(maxlen=50)  # Store recent embeddings
        self.identity_threshold = 0.6  # Cosine similarity threshold

        # Head pose estimation points
        self.HEAD_POSE_POINTS = [1, 33, 61, 199, 263, 291]  # Key facial landmarks

        # 3D model points for head pose
        self.model_points = np.array([
            [0.0, 0.0, 0.0],          # Nose tip
            [-30.0, -125.0, -30.0],   # Chin
            [-60.0, -70.0, -60.0],    # Left eye left corner
            [60.0, -70.0, -60.0],     # Right eye right corner
            [-40.0, 40.0, -50.0],     # Left Mouth corner
            [40.0, 40.0, -50.0]       # Right mouth corner
        ])

        # Camera matrix (will be set based on frame size)
        self.camera_matrix = None
        self.dist_coeffs = np.zeros((4, 1))

    def process_frame(self, frame):
        """Process frame for face detection and analysis."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        if self.camera_matrix is None:
            self._setup_camera_matrix(w, h)

        results = self.face_mesh.process(rgb)
        faces = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                face_data = self._analyze_face(face_landmarks, w, h)
                faces.append(face_data)

        return faces

    def _setup_camera_matrix(self, w, h):
        """Setup camera matrix for head pose estimation."""
        focal_length = w
        center = (w / 2, h / 2)
        self.camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

    def _analyze_face(self, face_landmarks, w, h):
        """Analyze single face for pose, identity, etc."""
        mesh_points = face_landmarks.landmark

        # Extract 2D points for head pose
        image_points = np.array([
            [mesh_points[self.HEAD_POSE_POINTS[0]].x * w, mesh_points[self.HEAD_POSE_POINTS[0]].y * h],
            [mesh_points[self.HEAD_POSE_POINTS[1]].x * w, mesh_points[self.HEAD_POSE_POINTS[1]].y * h],
            [mesh_points[self.HEAD_POSE_POINTS[2]].x * w, mesh_points[self.HEAD_POSE_POINTS[2]].y * h],
            [mesh_points[self.HEAD_POSE_POINTS[3]].x * w, mesh_points[self.HEAD_POSE_POINTS[3]].y * h],
            [mesh_points[self.HEAD_POSE_POINTS[4]].x * w, mesh_points[self.HEAD_POSE_POINTS[4]].y * h],
            [mesh_points[self.HEAD_POSE_POINTS[5]].x * w, mesh_points[self.HEAD_POSE_POINTS[5]].y * h]
        ], dtype=np.float64)

        # Calculate head pose
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points, image_points, self.camera_matrix, self.dist_coeffs
        )

        if success:
            rmat, _ = cv2.Rodrigues(rotation_vector)
            angles = cv2.RQDecomp3x3(rmat)[0]  # Get Euler angles
            pitch, yaw, roll = angles
        else:
            pitch = yaw = roll = 0

        # Calculate face embedding (simplified - using nose and eye positions)
        embedding = self._calculate_face_embedding(mesh_points, w, h)

        return {
            'landmarks': face_landmarks,
            'head_pose': {'pitch': pitch, 'yaw': yaw, 'roll': roll},
            'embedding': embedding,
            'bbox': self._get_face_bbox(mesh_points, w, h)
        }

    def _calculate_face_embedding(self, mesh_points, w, h):
        """Calculate simple face embedding from key landmarks."""
        key_points = [1, 33, 263, 61, 291, 199]  # Nose, eyes, mouth
        embedding = []
        for idx in key_points:
            point = mesh_points[idx]
            embedding.extend([point.x * w, point.y * h, point.z])
        return np.array(embedding)

    def _get_face_bbox(self, mesh_points, w, h):
        """Get bounding box of face."""
        x_coords = [p.x * w for p in mesh_points]
        y_coords = [p.y * h for p in mesh_points]
        return {
            'x': int(min(x_coords)),
            'y': int(min(y_coords)),
            'w': int(max(x_coords) - min(x_coords)),
            'h': int(max(y_coords) - min(y_coords))
        }

    def set_reference_identity(self, embedding):
        """Set reference face embedding for identity verification."""
        self.reference_embedding = embedding

    def verify_identity(self, current_embedding):
        """Verify if current face matches reference identity."""
        if self.reference_embedding is None:
            return True  # No reference set yet

        similarity = 1 - cosine(self.reference_embedding, current_embedding)
        self.embedding_history.append(similarity)

        # Check if identity is consistent over recent frames
        if len(self.embedding_history) >= 10:
            avg_similarity = np.mean(list(self.embedding_history))
            return avg_similarity > self.identity_threshold

        return similarity > self.identity_threshold

    def is_head_turned_away(self, head_pose, threshold=30):
        """Check if head is turned away from screen."""
        yaw, pitch = abs(head_pose['yaw']), abs(head_pose['pitch'])
        return yaw > threshold or pitch > threshold


class EyeTracker:
    """Handles eye gaze tracking, blink detection, and calibration."""

    def __init__(self):
        self.LEFT_IRIS_INDEXES = list(range(474, 478))
        self.RIGHT_IRIS_INDEXES = list(range(469, 473))
        self.LEFT_EYE_CORNERS = [33, 133]
        self.RIGHT_EYE_CORNERS = [362, 263]

        # Blink detection
        self.LEFT_EYE_POINTS = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_POINTS = [33, 160, 158, 133, 153, 144]
        self.EAR_THRESHOLD = 0.25
        self.EAR_CONSEC_FRAMES = 3
        self.blink_counter = 0
        self.blink_total = 0

        # Gaze calibration
        self.gaze_calibrated = False
        self.gaze_center_left = 0.5
        self.gaze_center_right = 0.5
        self.gaze_threshold = 0.3

        # Kalman filters for smoothing
        self.left_kalman = self._init_kalman_filter()
        self.right_kalman = self._init_kalman_filter()

        # Gaze history for smoothing
        self.gaze_history_left = deque(maxlen=10)
        self.gaze_history_right = deque(maxlen=10)

    def _init_kalman_filter(self):
        """Initialize Kalman filter for iris smoothing."""
        kf = cv2.KalmanFilter(4, 2)
        kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        kf.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) * 0.03
        kf.measurementNoiseCov = np.array([[1, 0], [0, 1]], np.float32) * 0.1
        return kf

    def calibrate_gaze(self, face_landmarks, w, h):
        """Calibrate gaze by having user look at center."""
        print("Calibrating gaze... Look directly at the center of the screen for 3 seconds.")

        ratios_left = []
        ratios_right = []

        start_time = time.time()
        while time.time() - start_time < 3:
            left_ratio = self._calculate_gaze_ratio(face_landmarks, self.LEFT_EYE_CORNERS, self.LEFT_IRIS_INDEXES, w, h)
            right_ratio = self._calculate_gaze_ratio(face_landmarks, self.RIGHT_EYE_CORNERS, self.RIGHT_IRIS_INDEXES, w, h)

            if left_ratio is not None:
                ratios_left.append(left_ratio)
            if right_ratio is not None:
                ratios_right.append(right_ratio)

            time.sleep(0.1)

        if ratios_left and ratios_right:
            self.gaze_center_left = np.mean(ratios_left)
            self.gaze_center_right = np.mean(ratios_right)
            self.gaze_calibrated = True
            print(f"Calibration complete. Centers: L={self.gaze_center_left:.3f}, R={self.gaze_center_right:.3f}")
        return self.gaze_calibrated

    def analyze_eyes(self, face_landmarks, w, h):
        """Analyze eyes for gaze direction and blink detection."""
        mesh_points = face_landmarks.landmark

        # Calculate gaze ratios
        left_ratio = self._calculate_gaze_ratio(mesh_points, self.LEFT_EYE_CORNERS, self.LEFT_IRIS_INDEXES, w, h)
        right_ratio = self._calculate_gaze_ratio(mesh_points, self.RIGHT_EYE_CORNERS, self.RIGHT_IRIS_INDEXES, w, h)

        # Smooth gaze ratios
        if left_ratio is not None:
            self.gaze_history_left.append(left_ratio)
        if right_ratio is not None:
            self.gaze_history_right.append(right_ratio)

        smoothed_left = np.mean(self.gaze_history_left) if self.gaze_history_left else left_ratio
        smoothed_right = np.mean(self.gaze_history_right) if self.gaze_history_right else right_ratio

        # Calculate iris centers with Kalman filtering
        left_iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in self.LEFT_IRIS_INDEXES])
        right_iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in self.RIGHT_IRIS_INDEXES])

        left_center_raw = np.mean(left_iris_points, axis=0).astype(int)
        right_center_raw = np.mean(right_iris_points, axis=0).astype(int)

        left_center = self._smooth_point(left_center_raw, self.left_kalman)
        right_center = self._smooth_point(right_center_raw, self.right_kalman)

        # Detect blinks
        left_ear = self._calculate_ear(mesh_points, self.LEFT_EYE_POINTS, w, h)
        right_ear = self._calculate_ear(mesh_points, self.RIGHT_EYE_POINTS, w, h)
        avg_ear = (left_ear + right_ear) / 2 if left_ear and right_ear else 0

        blink_detected = self._detect_blink(avg_ear)

        # Determine if looking at screen
        looking_at_screen = self._is_looking_at_screen(smoothed_left, smoothed_right)

        return {
            'gaze_ratios': {'left': smoothed_left, 'right': smoothed_right},
            'iris_centers': {'left': left_center, 'right': right_center},
            'looking_at_screen': looking_at_screen,
            'blink_detected': blink_detected,
            'ear': avg_ear,
            'blink_count': self.blink_total
        }

    def _calculate_gaze_ratio(self, mesh_points, eye_corners, iris_indexes, w, h):
        """Calculate horizontal gaze ratio."""
        try:
            eye_left = np.array([mesh_points[eye_corners[0]].x * w, mesh_points[eye_corners[0]].y * h])
            eye_right = np.array([mesh_points[eye_corners[1]].x * w, mesh_points[eye_corners[1]].y * h])

            iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in iris_indexes])
            iris_center = np.mean(iris_points, axis=0)

            eye_width = np.linalg.norm(eye_right - eye_left)
            iris_to_left = np.linalg.norm(iris_center - eye_left)
            iris_to_right = np.linalg.norm(iris_center - eye_right)

            if eye_width > 0:
                gaze_ratio = iris_to_left / (iris_to_left + iris_to_right)
                return gaze_ratio
        except:
            pass
        return None

    def _calculate_ear(self, mesh_points, eye_points, w, h):
        """Calculate Eye Aspect Ratio (EAR)."""
        try:
            # Vertical eye landmarks
            p2 = np.array([mesh_points[eye_points[1]].x * w, mesh_points[eye_points[1]].y * h])
            p3 = np.array([mesh_points[eye_points[2]].x * w, mesh_points[eye_points[2]].y * h])
            p4 = np.array([mesh_points[eye_points[3]].x * w, mesh_points[eye_points[3]].y * h])
            p5 = np.array([mesh_points[eye_points[4]].x * w, mesh_points[eye_points[4]].y * h])
            p6 = np.array([mesh_points[eye_points[5]].x * w, mesh_points[eye_points[5]].y * h])

            # Horizontal eye landmarks
            p1 = np.array([mesh_points[eye_points[0]].x * w, mesh_points[eye_points[0]].y * h])
            p7 = np.array([mesh_points[eye_points[6]].x * w, mesh_points[eye_points[6]].y * h])

            # Calculate distances
            ear = (np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)) / (2 * np.linalg.norm(p1 - p7))
            return ear
        except:
            return 0

    def _detect_blink(self, ear):
        """Detect eye blink based on EAR threshold."""
        if ear < self.EAR_THRESHOLD:
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.EAR_CONSEC_FRAMES:
                self.blink_total += 1
                blink_detected = True
            else:
                blink_detected = False
            self.blink_counter = 0

        return blink_detected if 'blink_detected' in locals() else False

    def _is_looking_at_screen(self, left_ratio, right_ratio):
        """Determine if eyes are looking at screen."""
        if left_ratio is None or right_ratio is None:
            return False

        left_on_screen = abs(left_ratio - self.gaze_center_left) < self.gaze_threshold
        right_on_screen = abs(right_ratio - self.gaze_center_right) < self.gaze_threshold

        return left_on_screen and right_on_screen

    def _smooth_point(self, point, kalman_filter):
        """Apply Kalman filtering to smooth point coordinates."""
        measurement = np.array([[np.float32(point[0])], [np.float32(point[1])]])
        kalman_filter.correct(measurement)
        prediction = kalman_filter.predict()
        return (int(prediction[0]), int(prediction[1]))


class ObjectDetector:
    """Handles detection of prohibited objects like phones, books, etc."""

    def __init__(self):
        # Load TFLite model (you'll need to download a suitable model)
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.labels = self._load_labels()

        # Try to load model, but don't fail if not available
        if TENSORFLOW_AVAILABLE:
            try:
                self._load_model()
            except:
                print("Warning: Object detection model not available. Object detection disabled.")
        else:
            print("Warning: TensorFlow not available. Object detection disabled.")

    def _load_model(self):
        """Load TensorFlow Lite model for object detection."""
        model_path = "models/efficientdet_lite0.tflite"
        if not os.path.exists(model_path):
            # Create models directory and download model if possible
            os.makedirs("models", exist_ok=True)
            print("Object detection model not found. Please download a TFLite model.")
            return

        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def _load_labels(self):
        """Load COCO labels or custom labels."""
        # Simplified labels - in practice, you'd load from a file
        return {
            0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane",
            5: "bus", 6: "train", 7: "truck", 8: "boat", 9: "traffic light",
            10: "fire hydrant", 11: "stop sign", 12: "parking meter", 13: "bench",
            14: "bird", 15: "cat", 16: "dog", 17: "horse", 18: "sheep", 19: "cow",
            20: "elephant", 21: "bear", 22: "zebra", 23: "giraffe", 24: "backpack",
            25: "umbrella", 26: "handbag", 27: "tie", 28: "suitcase", 29: "frisbee",
            30: "skis", 31: "snowboard", 32: "sports ball", 33: "kite", 34: "baseball bat",
            35: "baseball glove", 36: "skateboard", 37: "surfboard", 38: "tennis racket",
            39: "bottle", 40: "wine glass", 41: "cup", 42: "fork", 43: "knife",
            44: "spoon", 45: "bowl", 46: "banana", 47: "apple", 48: "sandwich",
            49: "orange", 50: "broccoli", 51: "carrot", 52: "hot dog", 53: "pizza",
            54: "donut", 55: "cake", 56: "chair", 57: "couch", 58: "potted plant",
            59: "bed", 60: "dining table", 61: "toilet", 62: "tv", 63: "laptop",
            64: "mouse", 65: "remote", 66: "keyboard", 67: "cell phone", 68: "microwave",
            69: "oven", 70: "toaster", 71: "sink", 72: "refrigerator", 73: "book",
            74: "clock", 75: "vase", 76: "scissors", 77: "teddy bear", 78: "hair drier",
            79: "toothbrush"
        }

    def detect_objects(self, frame):
        """Detect prohibited objects in frame."""
        if self.interpreter is None or not TENSORFLOW_AVAILABLE:
            return []

        # Preprocess frame
        input_shape = self.input_details[0]['shape']
        resized = cv2.resize(frame, (input_shape[2], input_shape[1]))
        input_data = np.expand_dims(resized, axis=0).astype(np.uint8)

        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        # Get results
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]

        detections = []
        h, w, _ = frame.shape

        for i in range(len(scores)):
            if scores[i] > 0.5:  # Confidence threshold
                class_id = int(classes[i])
                class_name = self.labels.get(class_id, f"class_{class_id}")

                # Check if it's a prohibited object
                if self._is_prohibited_object(class_name):
                    ymin, xmin, ymax, xmax = boxes[i]
                    bbox = {
                        'x': int(xmin * w),
                        'y': int(ymin * h),
                        'w': int((xmax - xmin) * w),
                        'h': int((ymax - ymin) * h)
                    }
                    detections.append({
                        'class': class_name,
                        'confidence': float(scores[i]),
                        'bbox': bbox
                    })

        return detections

    def _is_prohibited_object(self, class_name):
        """Check if object is prohibited during exam."""
        prohibited = [
            'cell phone', 'book', 'laptop', 'notebook', 'paper', 'pen', 'pencil',
            'bottle', 'cup', 'bowl', 'sandwich', 'pizza', 'donut', 'cake',
            'handbag', 'backpack', 'suitcase'
        ]
        return class_name.lower() in prohibited


class AudioMonitor:
    """Handles audio monitoring for suspicious sounds."""

    def __init__(self):
        self.audio_queue = queue.Queue()
        self.monitoring = False
        self.audio_thread = None

        # Audio analysis parameters
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.silence_threshold = 500
        self.voice_threshold = 1000

        # Try to initialize audio
        if PYAUDIO_AVAILABLE:
            self.audio = pyaudio.PyAudio()
            self.stream = None
        else:
            print("Warning: PyAudio not available. Audio monitoring disabled.")
            self.audio = None

    def start_monitoring(self):
        """Start audio monitoring thread."""
        if self.audio is None:
            return

        self.monitoring = True
        self.audio_thread = threading.Thread(target=self._monitor_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def stop_monitoring(self):
        """Stop audio monitoring."""
        self.monitoring = False
        if self.audio_thread:
            self.audio_thread.join()

    def _monitor_audio(self):
        """Monitor audio for suspicious sounds."""
        if self.audio is None or not PYAUDIO_AVAILABLE:
            return

        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            while self.monitoring:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)

                # Analyze audio
                rms = np.sqrt(np.mean(audio_data**2))
                suspicious = self._analyze_audio_features(audio_data, rms)

                if suspicious:
                    self.audio_queue.put({
                        'timestamp': time.time(),
                        'type': suspicious,
                        'rms': rms
                    })

        except Exception as e:
            print(f"Audio monitoring error: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

    def _analyze_audio_features(self, audio_data, rms):
        """Analyze audio features for suspicious activity."""
        if rms > self.voice_threshold:
            return "MULTIPLE_VOICES"
        elif rms > self.silence_threshold:
            return "BACKGROUND_NOISE"

        return None

    def get_audio_alerts(self):
        """Get any audio alerts from queue."""
        alerts = []
        while not self.audio_queue.empty():
            alerts.append(self.audio_queue.get())
        return alerts


class EventLogger:
    """Handles logging of suspicious events and evidence capture."""

    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(os.path.join(log_dir, "snapshots"), exist_ok=True)
        os.makedirs(os.path.join(log_dir, "clips"), exist_ok=True)

        # Setup logging
        log_file = os.path.join(log_dir, "malpractice_events.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.events = []
        self.session_start = time.time()

    def log_event(self, event_type, details, frame=None, evidence_type="snapshot"):
        """Log a suspicious event."""
        timestamp = time.time()
        event = {
            'timestamp': timestamp,
            'type': event_type,
            'details': details,
            'session_time': timestamp - self.session_start
        }

        self.events.append(event)
        logging.info(f"{event_type}: {details}")

        # Capture evidence if frame provided
        if frame is not None:
            self._capture_evidence(frame, event, evidence_type)

        return event

    def _capture_evidence(self, frame, event, evidence_type):
        """Capture snapshot or video clip as evidence."""
        timestamp_str = datetime.fromtimestamp(event['timestamp']).strftime("%Y%m%d_%H%M%S")

        if evidence_type == "snapshot":
            filename = f"snapshot_{timestamp_str}_{event['type']}.jpg"
            filepath = os.path.join(self.log_dir, "snapshots", filename)
            cv2.imwrite(filepath, frame)
            event['evidence_file'] = filepath

    def generate_report(self):
        """Generate summary report of the session."""
        report = {
            'session_duration': time.time() - self.session_start,
            'total_events': len(self.events),
            'events_by_type': {},
            'timeline': self.events
        }

        for event in self.events:
            event_type = event['type']
            if event_type not in report['events_by_type']:
                report['events_by_type'][event_type] = 0
            report['events_by_type'][event_type] += 1

        # Save report
        report_file = os.path.join(self.log_dir, "session_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return report


class MalpracticeDetectionSystem:
    """Main system integrating all detection components."""

    def __init__(self):
        # Initialize components
        self.face_tracker = FaceTracker()
        self.eye_tracker = EyeTracker()
        self.object_detector = ObjectDetector()
        self.audio_monitor = AudioMonitor()
        self.logger = EventLogger()

        # System state
        self.running = False
        self.calibrated = False
        self.reference_identity_set = False

        # Alert thresholds and timers
        self.look_away_threshold = 3.0  # seconds
        self.look_away_timer = 0
        self.last_face_count = 0
        self.eye_closure_timer = 0
        self.eye_closure_threshold = 2.0

        # UI components
        self.display_scale = 0.7
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        self._load_sounds()

    def _load_sounds(self):
        """Load alert sounds."""
        if PYGAME_AVAILABLE:
            try:
                # Create simple beep sounds (you'd normally load audio files)
                self.alert_sound = None  # pygame.mixer.Sound("alert.wav") if file exists
            except:
                self.alert_sound = None
        else:
            self.alert_sound = None

    def calibrate_system(self, frame):
        """Calibrate the system for the current user."""
        print("Starting system calibration...")

        # Wait for face detection
        faces = self.face_tracker.process_frame(frame)
        if not faces:
            return False, "No face detected for calibration"

        if len(faces) > 1:
            return False, "Multiple faces detected. Please ensure only one person is visible"

        # Set reference identity
        face = faces[0]
        self.face_tracker.set_reference_identity(face['embedding'])
        self.reference_identity_set = True

        # Calibrate gaze
        success = self.eye_tracker.calibrate_gaze(face['landmarks'], frame.shape[1], frame.shape[0])
        if not success:
            return False, "Gaze calibration failed"

        self.calibrated = True
        print("Calibration complete!")
        return True, "Calibration successful"

    def process_frame(self, frame):
        """Process a single frame through all detection systems."""
        alerts = []
        h, w, _ = frame.shape

        # Face detection and analysis
        faces = self.face_tracker.process_frame(frame)

        # Check face count
        if len(faces) == 0:
            alerts.append(("NO_FACE", "No face detected"))
        elif len(faces) > 1:
            alerts.append(("MULTIPLE_FACES", f"{len(faces)} faces detected"))

        # Process primary face if available
        primary_face = faces[0] if faces else None

        if primary_face:
            # Identity verification
            if self.reference_identity_set:
                identity_match = self.face_tracker.verify_identity(primary_face['embedding'])
                if not identity_match:
                    alerts.append(("IDENTITY_MISMATCH", "Face does not match reference identity"))

            # Head pose analysis
            if self.face_tracker.is_head_turned_away(primary_face['head_pose']):
                alerts.append(("HEAD_TURNED", "Head turned away from screen"))

            # Eye analysis
            eye_data = self.eye_tracker.analyze_eyes(primary_face['landmarks'], w, h)

            # Gaze analysis
            if not eye_data['looking_at_screen']:
                self.look_away_timer += 1/30  # Assuming 30 FPS
                if self.look_away_timer > self.look_away_threshold:
                    alerts.append(("LOOKING_AWAY", f"Looking away for {self.look_away_timer:.1f}s"))
            else:
                if self.look_away_timer > self.look_away_threshold:
                    self.logger.log_event("ATTENTION_RESUMED",
                                        f"After {self.look_away_timer:.1f} seconds away", frame)
                self.look_away_timer = 0

            # Blink analysis
            if eye_data['blink_detected']:
                self.logger.log_event("BLINK_DETECTED", "Eye blink detected", frame)

            # Eye closure detection
            if eye_data['ear'] < 0.2:  # Very low EAR indicates closed eyes
                self.eye_closure_timer += 1/30
                if self.eye_closure_timer > self.eye_closure_threshold:
                    alerts.append(("EYES_CLOSED", f"Eyes closed for {self.eye_closure_timer:.1f}s"))
            else:
                self.eye_closure_timer = 0

        # Object detection
        objects = self.object_detector.detect_objects(frame)
        for obj in objects:
            alerts.append(("PROHIBITED_OBJECT",
                         f"{obj['class']} detected (confidence: {obj['confidence']:.2f})"))

        # Audio alerts
        audio_alerts = self.audio_monitor.get_audio_alerts()
        for audio_alert in audio_alerts:
            alerts.append((audio_alert['type'], f"Audio: {audio_alert['type']}"))

        # Log alerts
        for alert_type, message in alerts:
            self.logger.log_event(alert_type, message, frame)

        # Play alert sound for critical alerts
        critical_alerts = ["MULTIPLE_FACES", "PROHIBITED_OBJECT", "IDENTITY_MISMATCH"]
        if any(alert[0] in critical_alerts for alert in alerts) and self.alert_sound:
            try:
                self.alert_sound.play()
            except:
                pass  # Sound playback failed

        return {
            'faces': faces,
            'eye_data': eye_data if primary_face else None,
            'objects': objects,
            'alerts': alerts,
            'frame': frame
        }

    def draw_overlays(self, frame, analysis_results):
        """Draw detection overlays on the frame."""
        display_frame = frame.copy()

        # Draw faces
        for face in analysis_results['faces']:
            bbox = face['bbox']
            cv2.rectangle(display_frame, (bbox['x'], bbox['y']),
                         (bbox['x'] + bbox['w'], bbox['y'] + bbox['h']), (0, 255, 0), 2)

            # Head pose info
            pose = face['head_pose']
            cv2.putText(display_frame, f"Yaw: {pose['yaw']:.1f}", (bbox['x'], bbox['y'] - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw eye data
        if analysis_results['eye_data']:
            eye_data = analysis_results['eye_data']

            # Iris centers
            for center in eye_data['iris_centers'].values():
                if center:
                    cv2.circle(display_frame, center, 3, (0, 255, 0), -1)

            # Gaze ratios
            ratios = eye_data['gaze_ratios']
            cv2.putText(display_frame, f"Gaze L: {ratios['left']:.3f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Gaze R: {ratios['right']:.3f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Blink count
            cv2.putText(display_frame, f"Blinks: {eye_data['blink_count']}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Draw detected objects
        for obj in analysis_results['objects']:
            bbox = obj['bbox']
            cv2.rectangle(display_frame, (bbox['x'], bbox['y']),
                         (bbox['x'] + bbox['w'], bbox['y'] + bbox['h']), (0, 0, 255), 2)
            cv2.putText(display_frame, f"{obj['class']}: {obj['confidence']:.2f}",
                       (bbox['x'], bbox['y'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Draw alerts
        y_offset = frame.shape[0] - 100
        for alert_type, message in analysis_results['alerts']:
            color = (0, 0, 255) if alert_type in ["MULTIPLE_FACES", "PROHIBITED_OBJECT"] else (0, 165, 255)
            cv2.putText(display_frame, f"ALERT: {message}", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset -= 30

        # Status indicators
        status_y = 120
        cv2.putText(display_frame, f"Calibrated: {self.calibrated}", (10, status_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if self.calibrated else (0, 0, 255), 2)
        cv2.putText(display_frame, f"Identity Set: {self.reference_identity_set}", (10, status_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if self.reference_identity_set else (0, 0, 255), 2)

        return display_frame

    def run_detection(self):
        """Main detection loop."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return

        print("Advanced Malpractice Detection System")
        print("Press 'c' to calibrate, 'r' to generate report, 'q' to quit")

        # Start audio monitoring
        self.audio_monitor.start_monitoring()

        calibration_done = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            # Calibration step
            if not calibration_done:
                success, message = self.calibrate_system(frame)
                if success:
                    calibration_done = True
                    print("System ready for monitoring")
                else:
                    cv2.putText(frame, f"Calibration: {message}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.imshow("Malpractice Detection - Calibration", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue

            # Process frame
            results = self.process_frame(frame)

            # Draw overlays
            display_frame = self.draw_overlays(frame, results)

            cv2.imshow("Advanced Malpractice Detection", display_frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                report = self.logger.generate_report()
                print(f"Report generated: {len(report['events'])} events logged")
                print(f"Events by type: {report['events_by_type']}")

        # Cleanup
        self.audio_monitor.stop_monitoring()
        cap.release()
        cv2.destroyAllWindows()

        # Generate final report
        final_report = self.logger.generate_report()
        print("Session complete. Final report saved.")
        print(f"Total events: {final_report['total_events']}")
        print(f"Session duration: {final_report['session_duration']:.1f} seconds")


if __name__ == "__main__":
    system = MalpracticeDetectionSystem()
    system.run_detection()