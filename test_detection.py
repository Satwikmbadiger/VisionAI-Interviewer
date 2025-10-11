#!/usr/bin/env python3
"""
Test script for MalpracticeDetection class
Tests core functionality without requiring webcam access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from malpractice_detection import MalpracticeDetection
import numpy as np

def test_initialization():
    """Test that the detector initializes correctly."""
    detector = MalpracticeDetection()
    assert detector.mp_face_mesh is not None
    assert detector.face_mesh is not None
    assert len(detector.LEFT_IRIS_INDEXES) == 4
    assert len(detector.RIGHT_IRIS_INDEXES) == 4
    print("✓ Initialization test passed")

def test_kalman_filter():
    """Test Kalman filter initialization."""
    detector = MalpracticeDetection()
    kf = detector._init_kalman_filter()
    assert kf is not None
    print("✓ Kalman filter test passed")

def test_gaze_calculation():
    """Test gaze ratio calculation with mock data."""
    detector = MalpracticeDetection()

    # Create mock mesh points (simulating MediaPipe landmarks)
    class MockPoint:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    # Mock mesh points - need to create enough points for all indices
    mock_mesh = [MockPoint(0, 0) for _ in range(478)]  # Create 478 points

    w, h = 640, 480

    # Left eye corners: left corner at x=0.3, right corner at x=0.4
    mock_mesh[33] = MockPoint(0.3, 0.4)   # LEFT_EYE_CORNERS[0]
    mock_mesh[133] = MockPoint(0.4, 0.4)  # LEFT_EYE_CORNERS[1]

    # Right eye corners: left corner at x=0.6, right corner at x=0.7
    mock_mesh[362] = MockPoint(0.6, 0.4)  # RIGHT_EYE_CORNERS[0]
    mock_mesh[263] = MockPoint(0.7, 0.4)  # RIGHT_EYE_CORNERS[1]

    # Left iris points (centered at 0.35)
    for idx in detector.LEFT_IRIS_INDEXES:
        mock_mesh[idx] = MockPoint(0.35, 0.4)

    # Right iris points (centered at 0.65)
    for idx in detector.RIGHT_IRIS_INDEXES:
        mock_mesh[idx] = MockPoint(0.65, 0.4)

    # Test gaze calculation
    left_ratio = detector._calculate_gaze_ratio(mock_mesh, detector.LEFT_EYE_CORNERS, detector.LEFT_IRIS_INDEXES, w, h)
    right_ratio = detector._calculate_gaze_ratio(mock_mesh, detector.RIGHT_EYE_CORNERS, detector.RIGHT_IRIS_INDEXES, w, h)

    assert left_ratio is not None
    assert right_ratio is not None
    assert 0.4 < left_ratio < 0.6  # Should be around 0.5 for centered iris
    assert 0.4 < right_ratio < 0.6
    print("✓ Gaze calculation test passed")

def test_looking_detection():
    """Test screen looking detection."""
    detector = MalpracticeDetection()

    # Test looking at screen (ratios around 0.5)
    assert detector._is_looking_at_screen(0.5, 0.5) == True
    assert detector._is_looking_at_screen(0.4, 0.6) == True

    # Test looking away (ratios far from 0.5)
    assert detector._is_looking_at_screen(0.1, 0.1) == False  # Looking far left
    assert detector._is_looking_at_screen(0.9, 0.9) == False  # Looking far right

    # Test None values
    assert detector._is_looking_at_screen(None, 0.5) == False
    assert detector._is_looking_at_screen(0.5, None) == False
    print("✓ Looking detection test passed")

def run_tests():
    """Run all tests."""
    print("Running MalpracticeDetection tests...")
    print()

    try:
        test_initialization()
        test_kalman_filter()
        test_gaze_calculation()
        test_looking_detection()

        print()
        print("🎉 All tests passed!")

    except Exception as e:
        import traceback
        print(f"❌ Test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)