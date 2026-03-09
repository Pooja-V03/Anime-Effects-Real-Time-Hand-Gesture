
import cv2
import numpy as np
import math
from utils.particles import ParticleSystem


def _add_glow(frame, cx, cy, radius, color_bgr, intensity=1.0):
    """Additive gaussian glow bloom around a point."""
    h, w = frame.shape[:2]
    glow = np.zeros((h, w, 3), dtype=np.float32)
    for r, strength in [
        (radius * 3,   0.06 * intensity),
        (radius * 2.2, 0.12 * intensity),
        (radius * 1.6, 0.22 * intensity),
        (radius * 1.2, 0.40 * intensity),
        (radius,       0.70 * intensity),
    ]:
        r = max(1, int(r))
        b = color_bgr[0] * strength
        g = color_bgr[1] * strength
        re= color_bgr[2] * strength
        cv2.circle(glow, (cx, cy), r, (b, g, re), -1)

    # gaussian blur for soft bloom
    ksize = max(3, (int(radius) * 4) | 1)   # must be odd
    glow  = cv2.GaussianBlur(glow, (ksize, ksize), 0)
    frame_f = frame.astype(np.float32)
    frame_f = np.clip(frame_f + glow * 255, 0, 255)
    return frame_f.astype(np.uint8)


class RasenganEffect:
    def __init__(self):
        self.particles       = ParticleSystem(400)
        self.storm_particles = ParticleSystem(200)
        self.angle           = 0.0
        self.active          = False
        self.fade            = 0.0
        self._shockwave_r    = 0
        self._shockwave_on   = False
        self._pulse          = 0.0

    def trigger(self):
        if not self.active:
            self._shockwave_r  = 0
            self._shockwave_on = True
        self.active = True

    def deactivate(self):
        self.active = False

    def draw(self, frame, palm_xy=None, dt=0.033):
        if not self.active and self.fade <= 0:
            return frame

        h, w = frame.shape[:2]

        if self.active:
            self.fade = min(1.0, self.fade + dt * 5)
        else:
            self.fade = max(0.0, self.fade - dt * 3)
            if self.fade <= 0:
                return frame

        if palm_xy is not None:
            cx = int(palm_xy[0] * w)
            cy = int(palm_xy[1] * h)
        else:
            cx, cy = w // 2, h // 2

        cx = max(120, min(w - 120, cx))
        cy = max(120, min(h - 120, cy))

        self.angle  += dt * 240
        self._pulse += dt * 7
        alpha = self.fade
        pulse_scale  = 1.0 + 0.10 * math.sin(self._pulse)
        R = max(5, int(60 * alpha * pulse_scale))

       
        frame = _add_glow(frame, cx, cy, R, (255, 120, 10), intensity=alpha * 1.2)

        # STEP 2
        if self._shockwave_on:
            self._shockwave_r += int(dt * 500)
            sw_a = max(0.0, 1.0 - self._shockwave_r / 220)
            if sw_a > 0 and self._shockwave_r > 0:
                sw_col = (int(220 * sw_a), int(160 * sw_a), int(30 * sw_a))
                cv2.circle(frame, (cx, cy), self._shockwave_r, sw_col, 3)
                # secondary ring
                if self._shockwave_r > 30:
                    cv2.circle(frame, (cx, cy), self._shockwave_r - 15,
                               (int(180*sw_a), int(100*sw_a), 10), 1)
            if self._shockwave_r > 220:
                self._shockwave_on = False

        #3
        ball = frame.copy()

        # deep blue fill
        cv2.circle(ball, (cx, cy), R, (160, 50, 5), -1)

        # spinning swirl bands
        for i in range(14):
            ba = math.radians(self.angle * (1 + i * 0.04) + i * 360 / 14)
            for t in np.linspace(0.05, 1.0, 35):
                r_t = t * (R - 2)
                a_t = ba + t * math.pi * 2.4
                x1  = int(cx + r_t * math.cos(a_t))
                y1  = int(cy + r_t * math.sin(a_t))
                ft  = 1.0 - t
                if 0 <= x1 < w and 0 <= y1 < h:
                    cv2.circle(ball, (x1, y1), max(1, int(3 * ft)),
                               (int(255*ft), int(180*ft*0.5), 8), -1)

        # counter swirl
        for i in range(7):
            ba = math.radians(-self.angle * 1.6 + i * 51)
            for t in np.linspace(0.0, 0.8, 22):
                r_t = t * (R - 6)
                a_t = ba + t * math.pi * 2.0
                x1  = int(cx + r_t * math.cos(a_t))
                y1  = int(cy + r_t * math.sin(a_t))
                if 0 <= x1 < w and 0 <= y1 < h:
                    cv2.circle(ball, (x1, y1), 2, (255, 255, 240), -1)

        # outer white ring
        cv2.circle(ball, (cx, cy), R,     (255, 255, 255), 3)
        cv2.circle(ball, (cx, cy), R - 4, (180, 220, 255), 2)

        # bright pulsing core
        core_r = max(2, int(20 * pulse_scale))
        cv2.circle(ball, (cx, cy), core_r + 8, (255, 230, 150), -1)
        cv2.circle(ball, (cx, cy), core_r + 3, (255, 250, 220), -1)
        cv2.circle(ball, (cx, cy), core_r,     (255, 255, 255), -1)

        cv2.addWeighted(ball, alpha, frame, 1 - alpha, 0, frame)

        # 4
        # outer blue corona
        frame = _add_glow(frame, cx, cy, R,      (255, 100, 5),  intensity=alpha * 0.8)
        # inner bright white core glow
        frame = _add_glow(frame, cx, cy, R // 3, (255, 255, 255), intensity=alpha * 1.5)

        # 5
        if self.active:
            for i in range(4):
                oa = math.radians(self.angle * 2.2 + i * 90)
                ox = cx + int((R + 18) * math.cos(oa))
                oy = cy + int((R + 18) * math.sin(oa))
                self.particles.emit(ox, oy, 3, (220, 240, 255),
                                    speed=2.5, spread=100,
                                    direction=int(math.degrees(oa) + 90),
                                    lifetime=0.3, size=2)
            outer_a = math.radians(self.angle * 0.6 + np.random.randint(0, 360))
            ox2 = cx + int((R + 35) * math.cos(outer_a))
            oy2 = cy + int((R + 35) * math.sin(outer_a))
            self.storm_particles.emit(ox2, oy2, 3, (80, 150, 255),
                                       speed=1.5, spread=360,
                                       lifetime=0.7, size=3)

        self.particles.update(dt)
        self.storm_particles.update(dt)
        self.particles.draw(frame)
        self.storm_particles.draw(frame)

        #6
        if self.active and alpha > 0.8:
            tint = np.zeros_like(frame, dtype=np.uint8)
            tint[:, :, 0] = 25
            cv2.addWeighted(tint, 0.1 * alpha, frame, 1.0, 0, frame)
            shake = int(3 * alpha)
            dx, dy = np.random.randint(-shake, shake + 1, 2)
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            frame = cv2.warpAffine(frame, M, (w, h))

        # 7
        if alpha > 0.3:
            _draw_jutsu_text(frame, "RASENGAN", (0, 180, 255), alpha, self._pulse)

        return frame


def _draw_jutsu_text(frame, text, color, alpha, pulse):
    h, w = frame.shape[:2]
    font  = cv2.FONT_HERSHEY_DUPLEX
    scale = 1.6
    thick = 3
    (tw, _), _ = cv2.getTextSize(text, font, scale, thick)
    x = (w - tw) // 2
    y = h - 38

    
    for offset, op in [(8, 0.2), (5, 0.4), (3, 0.6)]:
        ga = int(255 * alpha * op)
        cv2.putText(frame, text, (x - offset, y + offset),
                    font, scale, (ga, ga // 2, 5), thick + 5)

    pulse_b = 0.85 + 0.15 * math.sin(pulse)
    col = tuple(int(c * alpha * pulse_b) for c in color)
    cv2.putText(frame, text, (x + 2, y + 2), font, scale, (0, 0, 0), thick + 2)
    cv2.putText(frame, text, (x, y), font, scale, col, thick)
