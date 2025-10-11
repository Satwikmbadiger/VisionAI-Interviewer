#!/usr/bin/env python3
"""
Demo script for Advanced Malpractice Detection System
This script demonstrates the key features without requiring all dependencies
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import sys
import os

# Add the current directory to path so we can import the main module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from advanced_malpractice_detection import MalpracticeDetectionSystem
    FULL_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Full system not available: {e}")
    FULL_SYSTEM_AVAILABLE = False

def demo_basic_face_detection():
    """Demo basic face detection with MediaPipe."""
    print("=== Basic Face Detection Demo ===")

    # Initialize MediaPipe FaceMesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam")
        return

    print("Press 'q' to quit the demo")

    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        faces_detected = 0
        if results.multi_face_landmarks:
            faces_detected = len(results.multi_face_landmarks)

            for face_landmarks in results.multi_face_landmarks:
                # Draw face landmarks
                h, w, _ = frame.shape
                for landmark in face_landmarks.landmark:
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

                # Draw bounding box (simplified)
                x_coords = [int(p.x * w) for p in face_landmarks.landmark]
                y_coords = [int(p.y * h) for p in face_landmarks.landmark]
                cv2.rectangle(frame,
                            (min(x_coords), min(y_coords)),
                            (max(x_coords), max(y_coords)),
                            (0, 255, 0), 2)

        # Display info
        fps = frame_count / (time.time() - start_time) if time.time() - start_time > 0 else 0
        cv2.putText(frame, f"Faces: {faces_detected}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Face Detection Demo", frame)
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def demo_eye_tracking():
    """Demo basic eye tracking and gaze estimation."""
    print("=== Eye Tracking Demo ===")

    # Initialize MediaPipe FaceMesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    # Iris and eye landmarks
    LEFT_IRIS = list(range(474, 478))
    RIGHT_IRIS = list(range(469, 473))
    LEFT_EYE_CORNERS = [33, 133]
    RIGHT_EYE_CORNERS = [362, 263]

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam")
        return

    print("Look at different parts of the screen to see gaze tracking")
    print("Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            mesh_points = face_landmarks.landmark

            # Calculate iris centers
            left_iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in LEFT_IRIS])
            right_iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in RIGHT_IRIS])

            left_center = np.mean(left_iris_points, axis=0).astype(int)
            right_center = np.mean(right_iris_points, axis=0).astype(int)

            # Calculate gaze ratios
            left_ratio = calculate_gaze_ratio(mesh_points, LEFT_EYE_CORNERS, LEFT_IRIS, w, h)
            right_ratio = calculate_gaze_ratio(mesh_points, RIGHT_EYE_CORNERS, RIGHT_IRIS, w, h)

            # Draw iris centers
            cv2.circle(frame, tuple(left_center), 3, (0, 255, 0), -1)
            cv2.circle(frame, tuple(right_center), 3, (0, 255, 0), -1)

            # Draw crosshairs
            cv2.line(frame, (left_center[0] - 10, left_center[1]), (left_center[0] + 10, left_center[1]), (0, 255, 0), 1)
            cv2.line(frame, (left_center[0], left_center[1] - 10), (left_center[0], left_center[1] + 10), (0, 255, 0), 1)

            cv2.line(frame, (right_center[0] - 10, right_center[1]), (right_center[0] + 10, right_center[1]), (0, 255, 0), 1)
            cv2.line(frame, (right_center[0], right_center[1] - 10), (right_center[0], right_center[1] + 10), (0, 255, 0), 1)

            # Display gaze ratios
            cv2.putText(frame, f"Left Gaze: {left_ratio:.3f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Right Gaze: {right_ratio:.3f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Determine looking direction
            avg_gaze = (left_ratio + right_ratio) / 2
            if avg_gaze < 0.4:
                direction = "Looking LEFT"
            elif avg_gaze > 0.6:
                direction = "Looking RIGHT"
            else:
                direction = "Looking CENTER"

            cv2.putText(frame, direction, (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Eye Tracking Demo", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def calculate_gaze_ratio(mesh_points, eye_corners, iris_indexes, w, h):
    """Calculate horizontal gaze ratio."""
    try:
        eye_left = np.array([mesh_points[eye_corners[0]].x * w, mesh_points[eye_corners[0]].y * h])
        eye_right = np.array([mesh_points[eye_corners[1]].x * w, mesh_points[eye_corners[1]].y * h])

        iris_points = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in iris_indexes])
        iris_center = np.mean(iris_points, axis=0)

        eye_width = np.linalg.norm(eye_right - eye_left)
        iris_to_left = np.linalg.norm(iris_center - eye_left)

        if eye_width > 0:
            gaze_ratio = iris_to_left / eye_width
            return gaze_ratio
    except:
        pass
    return 0.5  # Default center

def demo_blink_detection():
    """Demo eye blink detection using EAR."""
    print("=== Blink Detection Demo ===")

    # Initialize MediaPipe FaceMesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    # Eye landmarks for EAR calculation
    LEFT_EYE = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE = [33, 160, 158, 133, 153, 144]

    EAR_THRESHOLD = 0.25
    CONSECUTIVE_FRAMES = 3

    blink_counter = 0
    total_blinks = 0

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam")
        return

    print("Blink your eyes to test detection")
    print("Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            mesh_points = face_landmarks.landmark

            # Calculate EAR for both eyes
            left_ear = calculate_ear(mesh_points, LEFT_EYE, w, h)
            right_ear = calculate_ear(mesh_points, RIGHT_EYE, w, h)
            avg_ear = (left_ear + right_ear) / 2

            # Detect blink
            if avg_ear < EAR_THRESHOLD:
                blink_counter += 1
            else:
                if blink_counter >= CONSECUTIVE_FRAMES:
                    total_blinks += 1
                blink_counter = 0

            # Display EAR and blink info
            cv2.putText(frame, f"EAR: {avg_ear:.3f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Blinks: {total_blinks}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Counter: {blink_counter}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Draw eye landmarks
            for eye_landmarks in [LEFT_EYE, RIGHT_EYE]:
                for idx in eye_landmarks:
                    point = mesh_points[idx]
                    x, y = int(point.x * w), int(point.y * h)
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        cv2.imshow("Blink Detection Demo", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def calculate_ear(mesh_points, eye_points, w, h):
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
        return 1.0

def run_full_system():
    """Run the full malpractice detection system."""
    if not FULL_SYSTEM_AVAILABLE:
        print("Full system not available. Please install all dependencies.")
        return

    print("=== Full Malpractice Detection System ===")
    system = MalpracticeDetectionSystem()
    system.run_detection()

def main():
    """Main demo menu."""
    print("Advanced Malpractice Detection System - Demo")
    print("=" * 50)

    while True:
        print("\nAvailable Demos:")
        print("1. Basic Face Detection")
        print("2. Eye Tracking & Gaze Estimation")
        print("3. Blink Detection")
        print("4. Full System (requires all dependencies)")
        print("5. Exit")

        try:
            choice = input("\nSelect demo (1-5): ").strip()

            if choice == '1':
                demo_basic_face_detection()
            elif choice == '2':
                demo_eye_tracking()
            elif choice == '3':
                demo_blink_detection()
            elif choice == '4':
                run_full_system()
            elif choice == '5':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-5.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()