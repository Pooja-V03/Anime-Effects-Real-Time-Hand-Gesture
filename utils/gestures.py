"""
Gesture detection - Simple 3 effect system
RIGHT hand open palm  Rasengan
LEFT  hand open palm  Chidori
BOTH  hands open      Water Breathing
"""
import numpy as np
import time


class GestureDetector:
    def __init__(self, lock_time=0.4):
        self.lock_time   = lock_time
        self._hold_start = {}
        self._locked     = {}

    @staticmethod
    def _fingers_up(hand_lms):
        up = []
        up.append(hand_lms.landmark[4].x < hand_lms.landmark[3].x)
        for tip, joint in [(8,6), (12,10), (16,14), (20,18)]:
            up.append(hand_lms.landmark[tip].y < hand_lms.landmark[joint].y)
        return up

    @staticmethod
    def _palm_center(hand_lms):
        pts = [hand_lms.landmark[i] for i in [0,5,9,13,17]]
        x = np.mean([p.x for p in pts])
        y = np.mean([p.y for p in pts])
        return x, y

    @staticmethod
    def _is_open_palm(hand_lms):
        """4 main fingers upar hain"""
        fu = GestureDetector._fingers_up(hand_lms)
        return fu[1] and fu[2] and fu[3] and fu[4]

    def _check_effects(self, hands_results):
        """
        Returns:
          rasengan: (active, palm_xy)
          chidori:  (active, palm_xy)
          water:    (active, None)
        """
        rasengan_data = None
        chidori_data  = None
        right_open    = False
        left_open     = False

        if not hands_results or not hands_results.multi_hand_landmarks:
            return False, None, False, None, False

        for i, hlms in enumerate(hands_results.multi_hand_landmarks):
            label = hands_results.multi_handedness[i].classification[0].label
            palm  = self._palm_center(hlms)
            if self._is_open_palm(hlms):
                if label == "Right":
                    right_open   = True
                    rasengan_data = palm
                elif label == "Left":
                    left_open    = True
                    chidori_data  = palm

        # Both hands open = Water (overrides single hand effects)
        water_active = right_open and left_open

        # Single hand only
        ra_active = right_open and not left_open
        ch_active = left_open  and not right_open

        return ra_active, rasengan_data, ch_active, chidori_data, water_active

    def _update_lock(self, name, active):
        now = time.time()
        if active:
            if name not in self._hold_start:
                self._hold_start[name] = now
            if now - self._hold_start[name] >= self.lock_time:
                self._locked[name] = True
        else:
            self._hold_start.pop(name, None)
            self._locked[name] = False
        return self._locked.get(name, False)

    def detect(self, hands_results, pose_results, face_results):
        ra_active, ra_data, ch_active, ch_data, wa_active = \
            self._check_effects(hands_results)

        return {
            'rasengan':  (self._update_lock('rasengan', ra_active),  ra_data),
            'chidori':   (self._update_lock('chidori',  ch_active),  ch_data),
            'water':     (self._update_lock('water',    wa_active),  None),
            'amaterasu': (False, None),
            'clone':     (False, None),
        }
