#!/usr/bin/env python3
"""
Setup script for Advanced Malpractice Detection System
Handles dependency installation and system verification
"""

import sys
import subprocess
import os
import platform

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Success")
            return True
        else:
            print(f"✗ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.8+")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")

    # Try to install core dependencies first
    core_packages = [
        "opencv-python",
        "mediapipe",
        "numpy",
        "scipy"
    ]

    optional_packages = [
        ("tensorflow", "TensorFlow (for object detection)"),
        ("tflite-runtime", "TFLite runtime (alternative to TensorFlow)"),
        ("pyaudio", "PyAudio (for audio monitoring)"),
        ("pygame", "Pygame (for audio alerts)"),
        ("scikit-learn", "Scikit-learn (for advanced features)"),
        ("matplotlib", "Matplotlib (for visualization)"),
        ("pillow", "Pillow (for image processing)")
    ]

    # Install core packages
    core_cmd = f"{sys.executable} -m pip install {' '.join(core_packages)}"
    if not run_command(core_cmd, "Installing core dependencies"):
        return False

    # Install optional packages
    print("\nInstalling optional dependencies...")
    for package, description in optional_packages:
        cmd = f"{sys.executable} -m pip install {package}"
        run_command(cmd, f"Installing {description}")
        # Don't fail if optional packages can't be installed

    return True

def setup_directories():
    """Create necessary directories."""
    print("\nSetting up directories...")
    directories = [
        "logs",
        "logs/snapshots",
        "logs/clips",
        "models"
    ]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        except Exception as e:
            print(f"✗ Failed to create {directory}: {e}")
            return False

    return True

def download_models():
    """Download pre-trained models (optional)."""
    print("\nSetting up models...")
    print("Note: Object detection models need to be downloaded manually.")
    print("Place TFLite models in the 'models/' directory.")
    print("Recommended: EfficientDet Lite models from TensorFlow Hub")
    return True

def verify_installation():
    """Verify that key components can be imported."""
    print("\nVerifying installation...")

    test_imports = [
        ("cv2", "OpenCV"),
        ("mediapipe", "MediaPipe"),
        ("numpy", "NumPy"),
        ("scipy.spatial.distance", "SciPy")
    ]

    optional_imports = [
        ("tensorflow", "TensorFlow"),
        ("tflite_runtime", "TFLite Runtime"),
        ("pygame", "Pygame"),
        ("pyaudio", "PyAudio")
    ]

    success_count = 0
    total_count = len(test_imports)

    # Test core imports
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✓ {name} available")
            success_count += 1
        except ImportError:
            print(f"✗ {name} not available")

    # Test optional imports
    print("\nOptional components:")
    for module, name in optional_imports:
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError:
            print(f"- {name} not available (optional)")

    if success_count == total_count:
        print(f"\n🎉 Core installation successful! ({success_count}/{total_count} components)")
        return True
    else:
        print(f"\n⚠️  Partial installation. ({success_count}/{total_count} core components)")
        print("Some features may not work. Check error messages above.")
        return False

def create_config_file():
    """Create a basic configuration file."""
    config_content = '''# Advanced Malpractice Detection Configuration
# Modify these values to customize system behavior

[DETECTION_SETTINGS]
max_num_faces = 3
min_detection_confidence = 0.7
min_tracking_confidence = 0.7

[ALERT_THRESHOLDS]
look_away_threshold = 3.0
eye_closure_threshold = 2.0
gaze_threshold = 0.3
ear_threshold = 0.25
blink_consecutive_frames = 3

[IDENTITY_SETTINGS]
identity_threshold = 0.6
embedding_history_size = 50

[AUDIO_SETTINGS]
voice_threshold = 1000
silence_threshold = 500
sample_rate = 44100
chunk_size = 1024

[UI_SETTINGS]
display_scale = 0.7
alert_sound_enabled = true

[LOGGING_SETTINGS]
log_level = INFO
evidence_capture = true
session_reports = true
'''

    try:
        with open('config.ini', 'w') as f:
            f.write(config_content)
        print("✓ Created config.ini with default settings")
        return True
    except Exception as e:
        print(f"✗ Failed to create config file: {e}")
        return False

def main():
    """Main setup function."""
    print("Advanced Malpractice Detection System Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("Failed to install core dependencies. Please check your Python environment.")
        sys.exit(1)

    # Setup directories
    if not setup_directories():
        print("Failed to create necessary directories.")
        sys.exit(1)

    # Download models (informational)
    download_models()

    # Create config file
    create_config_file()

    # Verify installation
    if verify_installation():
        print("\n" + "=" * 50)
        print("Setup complete! You can now run:")
        print("  python demo.py              # Run demos")
        print("  python advanced_malpractice_detection.py  # Run full system")
        print("\nFor help, see ADVANCED_README.md")
    else:
        print("\nSetup completed with warnings. Some features may not work.")
        sys.exit(1)

if __name__ == "__main__":
    # Check if running on supported platform
    system = platform.system().lower()
    if system not in ['windows', 'linux', 'darwin']:
        print(f"Warning: Platform '{system}' may not be fully supported.")

    main()