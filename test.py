import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe FaceMesh with iris tracking enabled
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,  # <== THIS enables iris tracking!
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Indexes for iris center points
LEFT_IRIS_INDEXES = list(range(474, 478))
RIGHT_IRIS_INDEXES = list(range(469, 473))

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            mesh_points = face_landmarks.landmark

            # Get left and right iris center by averaging the 4 iris points
            left_iris = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in LEFT_IRIS_INDEXES])
            right_iris = np.array([(mesh_points[p].x * w, mesh_points[p].y * h) for p in RIGHT_IRIS_INDEXES])

            left_center = np.mean(left_iris, axis=0).astype(int)
            right_center = np.mean(right_iris, axis=0).astype(int)

            # Draw iris centers
            cv2.circle(frame, tuple(left_center), 3, (0, 255, 0), -1)
            cv2.circle(frame, tuple(right_center), 3, (0, 255, 0), -1)

            # Optional: draw crosshair lines
            cv2.line(frame, (left_center[0] - 10, left_center[1]), (left_center[0] + 10, left_center[1]), (0, 255, 0), 1)
            cv2.line(frame, (left_center[0], left_center[1] - 10), (left_center[0], left_center[1] + 10), (0, 255, 0), 1)

            cv2.line(frame, (right_center[0] - 10, right_center[1]), (right_center[0] + 10, right_center[1]), (0, 255, 0), 1)
            cv2.line(frame, (right_center[0], right_center[1] - 10), (right_center[0], right_center[1] + 10), (0, 255, 0), 1)

    cv2.imshow("High Accuracy Iris Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
