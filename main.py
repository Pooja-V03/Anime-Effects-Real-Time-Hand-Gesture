"""
Anime Effects System – main.py
================================
Controls:
  2    Rasengan
  4    Water Breathing
  5    Chidori
  R    Reset all effects
  Q    Quit
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.gestures    import GestureDetector
from effects.rasengan  import RasenganEffect
from effects.chidori   import ChidoriEffect
from effects.water     import WaterAuraEffect

# ── MediaPipe setup ───────────────────────────────────────────────────────────
mp_hands     = mp.solutions.hands
mp_pose      = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
mp_drawing   = mp.solutions.drawing_utils

hands     = mp_hands.Hands(max_num_hands=2,
                             min_detection_confidence=0.6,
                             min_tracking_confidence=0.6)
pose      = mp_pose.Pose(min_detection_confidence=0.5,
                          min_tracking_confidence=0.5)
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1,
                                   min_detection_confidence=0.5,
                                   min_tracking_confidence=0.5)

# ── Effects ───────────────────────────────────────────────────────────────────
fx_rasengan = RasenganEffect()
fx_water    = WaterAuraEffect()
fx_chidori  = ChidoriEffect()

detector = GestureDetector(lock_time=0.5)

# ── Webcam at 720p ────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
if not cap.isOpened():
    raise RuntimeError("Cannot open webcam.")

prev_time = time.time()

# ── HUD definitions ───────────────────────────────────────────────────────────
EFFECTS_INFO = {
    'rasengan': ("RASENGAN",        "Right hand open"),
    'water':    ("WATER BREATHING", "Both hands open"),
    'chidori':  ("CHIDORI",         "Left hand open"),
}
EFFECT_COLORS = {
    'rasengan': (255, 180, 50),
    'water':    (200, 150, 30),
    'chidori':  (220, 220, 255),
}


def draw_hud(frame, gestures, fps):
    h, w = frame.shape[:2]

    # FPS
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 128), 2)

    # Effect status panel (top-right)
    panel_w = 260
    panel_h = 100
    panel = frame[0:panel_h, w-panel_w:w].copy()
    cv2.rectangle(panel, (0, 0), (panel_w, panel_h), (0, 0, 0), -1)
    cv2.addWeighted(panel, 0.5, frame[0:panel_h, w-panel_w:w], 0.5, 0,
                    frame[0:panel_h, w-panel_w:w])

    for i, (key, (name, hint)) in enumerate(EFFECTS_INFO.items()):
        locked, _ = gestures.get(key, (False, None))
        col  = EFFECT_COLORS[key] if locked else (80, 80, 80)
        mark = ">" if locked else "-"
        cv2.putText(frame, f"{mark} {name}",
                    (w - panel_w + 8, 22 + i * 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50,
                    tuple(int(c) for c in col), 1)

    # Bottom hint
    cv2.putText(frame, "2:Rasengan  4:Water  5:Chidori  Q:Quit",
                (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 160, 160), 1)


# ── Main loop ─────────────────────────────────────────────────────────────────
print("Anime Effects started! Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w  = frame.shape[:2]
    now   = time.time()
    dt    = max(0.001, now - prev_time)
    prev_time = now
    fps   = 1.0 / dt

    # MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    hands_res = hands.process(rgb)
    pose_res  = pose.process(rgb)
    face_res  = face_mesh.process(rgb)
    rgb.flags.writeable = True

    # Gestures
    gestures = detector.detect(hands_res, pose_res, face_res)

    rasen_lock, ra_data = gestures['rasengan']
    chidori_lock, ch_data = gestures['chidori']
    water_lock, _ = gestures['water']

    # ── Trigger logic: dono haath = sirf water ────────────────────────────────
    if water_lock:
        fx_water.trigger()
        fx_rasengan.deactivate()
        fx_chidori.deactivate()
    else:
        fx_water.deactivate()
        if rasen_lock:
            fx_rasengan.trigger()
        else:
            fx_rasengan.deactivate()

        if chidori_lock:
            fx_chidori.trigger()
        else:
            fx_chidori.deactivate()

    # Keyboard shortcuts
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('2'):
        fx_rasengan.trigger()
    elif key == ord('4'):
        fx_water.trigger()
    elif key == ord('5'):
        fx_chidori.trigger()
    elif key == ord('r'):
        fx_rasengan.deactivate()
        fx_water.deactivate()
        fx_chidori.deactivate()

    # ── Render ────────────────────────────────────────────────────────────────
    pose_lms = pose_res.pose_landmarks if pose_res else None
    frame = fx_water.draw(frame, pose_lms=pose_lms, dt=dt)
    frame = fx_rasengan.draw(frame, palm_xy=ra_data, dt=dt)
    frame = fx_chidori.draw(frame, wrist_xy=ch_data, dt=dt)

    # HUD
    draw_hud(frame, gestures, fps)

    cv2.imshow("Anime Effects", frame)

# Cleanup
cap.release()
hands.close()
pose.close()
face_mesh.close()
cv2.destroyAllWindows()
print("Closed.")
