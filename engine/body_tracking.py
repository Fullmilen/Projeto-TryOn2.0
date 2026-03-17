import cv2
import mediapipe as mp

# ==========================================================
# INICIALIZAÇÃO DO MEDIAPIPE
# ==========================================================

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

mp_drawing = mp.solutions.drawing_utils


# ==========================================================
# DETECTAR POSE
# ==========================================================

def detect_pose(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    return results


# ==========================================================
# DESENHAR ESQUELETO
# ==========================================================

def draw_pose(frame, results):
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )
    return frame