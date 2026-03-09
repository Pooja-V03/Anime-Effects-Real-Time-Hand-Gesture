
import cv2
import numpy as np
import time
from utils.particles import ParticleSystem, LightningSystem


class ChidoriEffect:
    def __init__(self):
        self.particles = ParticleSystem(250)
        self.active    = False
        self.fade      = 0.0
        self._flicker  = 0.0

    def trigger(self, wrist_xy=None):
        self.active = True

    def deactivate(self):
        self.active = False

    def draw(self, frame, wrist_xy=None, dt=0.033):
        if not self.active and self.fade <= 0:
            return frame

        h, w = frame.shape[:2]

        if self.active:
            self.fade = min(1.0, self.fade + dt * 5)
        else:
            self.fade = max(0.0, self.fade - dt * 4)
            if self.fade <= 0:
                return frame

        # Follow left hand
        if wrist_xy is not None:
            cx = int(wrist_xy[0] * w)
            cy = int(wrist_xy[1] * h)
        else:
            cx = int(w * 0.25)
            cy = int(h * 0.5)

        cx = max(60, min(w - 60, cx))
        cy = max(60, min(h - 60, cy))

        alpha = self.fade

        # Screen flicker
        self._flicker += dt * 15
        flicker_val = int((np.sin(self._flicker * np.pi) * 0.5 + 0.5) * 25 * alpha)
        if flicker_val > 0:
            bright = np.ones_like(frame, dtype=np.uint8) * flicker_val
            cv2.add(frame, bright, frame)

        # Glow around hand
        overlay = frame.copy()
        for r, a_val in [(80,0.10),(60,0.18),(40,0.28),(22,0.45)]:
            gv = int(255 * a_val * alpha)
            cv2.circle(overlay, (cx,cy), r, (gv, gv, min(255,gv+50)), -1)
        cv2.addWeighted(overlay, 0.65*alpha, frame, 1-0.65*alpha, 0, frame)

        # Lightning
        LightningSystem.draw_burst(frame, cx, cy, count=8,
                                    radius=int(95*alpha), color=(200,220,255))
        LightningSystem.draw_burst(frame, cx, cy, count=5,
                                    radius=int(50*alpha), color=(255,255,255))

        # Particles
        if self.active:
            self.particles.emit(cx, cy, 8, (180,200,255),
                                speed=3, spread=360, lifetime=0.4, size=2)
        self.particles.update(dt)
        self.particles.draw(frame)

        if alpha > 0.3:
            _draw_text(frame, "CHIDORI", (180,200,255), alpha)

        return frame


def _draw_text(frame, text, color, alpha):
    h, w = frame.shape[:2]
    font  = cv2.FONT_HERSHEY_DUPLEX
    scale = 1.4; thick = 3
    (tw,_),_ = cv2.getTextSize(text, font, scale, thick)
    x = (w-tw)//2; y = h-40
    cv2.putText(frame, text, (x+3,y+3), font, scale, (0,0,0), thick+2)
    cv2.putText(frame, text, (x,y), font, scale,
                tuple(int(c*alpha) for c in color), thick)
