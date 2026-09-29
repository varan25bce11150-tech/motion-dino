# vision/gesture.py
import cv2
import numpy as np
from collections import deque

# Import MediaPipe pose submodules safely
try:
    import mediapipe.python.solutions.pose as mp_pose
    import mediapipe.python.solutions.drawing_utils as mp_drawing
except ImportError:
    try:
        import mediapipe as mp
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
    except AttributeError:
        raise ImportError(
            "MediaPipe solutions module missing. Run: pip install mediapipe==0.10.14"
        )

class GestureDetector:
    def __init__(self):
        self.mp_pose = mp_pose
        self.mp_drawing = mp_drawing
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            model_complexity=0  # Lightweight mode for low latency
        )
        
        # Calibration state
        self.is_calibrated = False
        self.baseline_hip_y = None
        self.baseline_torso_height = None
        
        # Smoothing filter
        self.history_size = 5
        self.hip_y_history = deque(maxlen=self.history_size)
        
        # Jump state & debouncing
        self.cooldown_counter = 0
        self.cooldown_frames = 12  # Frames to wait before next jump trigger

    def process_frame(self, frame):
        """Processes RGB frame with MediaPipe Pose and draws landmarks."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        
        # Draw skeleton on image
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
            
        return results, frame

    def calibrate(self, landmarks):
        """Captures neutral standing position to set relative thresholds."""
        if not landmarks:
            return False
            
        # Extract landmark normalized Y positions (0 top -> 1 bottom)
        left_hip = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].y
        right_hip = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP].y
        left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y
        right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        
        avg_hip_y = (left_hip + right_hip) / 2.0
        avg_shoulder_y = (left_shoulder + right_shoulder) / 2.0
        
        self.baseline_hip_y = avg_hip_y
        self.baseline_torso_height = abs(avg_hip_y - avg_shoulder_y)
        self.is_calibrated = True
        self.hip_y_history.clear()
        return True

    def detect_jump(self, landmarks):
        """Returns True if a jump gesture is recognized."""
        if not landmarks or not self.is_calibrated:
            return False

        # Manage debouncing cooldown
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
            return False

        left_hip = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP].y
        right_hip = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP].y
        current_hip_y = (left_hip + right_hip) / 2.0

        # Push to moving average buffer
        self.hip_y_history.append(current_hip_y)
        
        if len(self.hip_y_history) < self.history_size:
            return False

        smoothed_hip_y = float(np.mean(self.hip_y_history))
        
        # Jump threshold: Move upward by at least 25% of torso height
        jump_threshold = self.baseline_hip_y - (self.baseline_torso_height * 0.25)

        if smoothed_hip_y < jump_threshold:
            self.cooldown_counter = self.cooldown_frames
            return True

        return False