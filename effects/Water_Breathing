
import cv2
import numpy as np
import math
import time
from utils.particles import ParticleSystem


class WaterAuraEffect:
    def __init__(self):
        self.particles = ParticleSystem(200)
        self.active    = False
        self.fade      = 0.0
        self._t        = 0.0
        self._slashes  = []
        self._next_slash = 0.0

    def trigger(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def _spawn_slash(self, cx, cy, w, h):
        side    = 1 if np.random.rand() > 0.5 else -1
        start_a = np.random.uniform(0, 2*math.pi)
        sweep   = np.random.uniform(math.pi*0.9, math.pi*1.5) * side
        rx      = np.random.randint(int(w*0.20), int(w*0.35))
        ry      = np.random.randint(int(h*0.25), int(h*0.45))
        return {
            'cx': cx, 'cy': cy, 'rx': rx, 'ry': ry,
            'start_a': start_a, 'sweep': sweep,
            'thickness': np.random.randint(8, 22),
            'lifetime': np.random.uniform(0.5, 1.0),
            'age': 0.0,
            'cyan': np.random.rand(),
        }

    def draw(self, frame, pose_lms=None, dt=0.033):
        if not self.active and self.fade <= 0:
            return frame

        h, w = frame.shape[:2]

        if self.active:
            self.fade = min(1.0, self.fade + dt*3)
        else:
            self.fade = max(0.0, self.fade - dt*2)
            if self.fade <= 0:
                self._slashes = []
                return frame

        self._t += dt
        alpha = self.fade

        # Body center
        if pose_lms is not None:
            lms = pose_lms.landmark
            vis = [l for l in lms if l.visibility > 0.4]
            if vis:
                cx = int(np.mean([l.x*w for l in vis]))
                cy = int(np.mean([l.y*h for l in vis]))
            else:
                cx, cy = w//2, h//2
        else:
            cx, cy = w//2, h//2

        # Spawn slashes
        self._next_slash -= dt
        if self._next_slash <= 0 and self.active:
            self._next_slash = 0.10
            self._slashes.append(self._spawn_slash(cx, cy, w, h))

        # Blue screen tint
        tint = np.zeros_like(frame, dtype=np.uint8)
        tint[:,:,0] = 50
        cv2.addWeighted(tint, 0.20*alpha, frame, 1.0, 0, frame)

        # Draw slashes
        dead = []
        for i, sl in enumerate(self._slashes):
            sl['age'] += dt
            if sl['age'] > sl['lifetime']:
                dead.append(i)
                continue

            p = sl['age'] / sl['lifetime']
            # Fade in/out
            sl_a = (p / 0.2) if p < 0.2 else (1.0 - (p-0.2)/0.8)
            sl_a = max(0.0, min(1.0, sl_a)) * alpha

            # Color: deep blue to cyan
            ct = sl['cyan']
            B = int(255*(1-ct*0.3))
            G = int((60 + 160*ct))
            R = int(10  + 10*ct)

            # Grow sweep over time
            sweep = sl['sweep'] * min(1.0, p * 3.0)

            n = 80
            pts = []
            for j in range(n):
                t2    = j / (n-1)
                angle = sl['start_a'] + sweep * t2
                x = int(sl['cx'] + sl['rx'] * math.cos(angle))
                y = int(sl['cy'] + sl['ry'] * math.sin(angle))
                pts.append((x, y, angle, t2))

            for j, (x, y, angle, t2) in enumerate(pts):
                if not (0 <= x < w and 0 <= y < h):
                    continue
                # Tapered thickness
                taper = 1.0 - abs(t2 - 0.5) * 1.6
                taper = max(0.05, taper)
                thick = max(1, int(sl['thickness'] * taper * sl_a))

                # Main water
                col = (int(B*sl_a), int(G*sl_a), int(R*sl_a))
                cv2.circle(frame, (x,y), thick, col, -1)

                # White foam on edges
                if j % 4 == 0 and sl_a > 0.3:
                    foam_a = sl_a * 0.8
                    fc = (int(255*foam_a), int(255*foam_a), int(255*foam_a))
                    fx = x + int(math.cos(angle + math.pi/2) * (thick+2))
                    fy = y + int(math.sin(angle + math.pi/2) * (thick+2))
                    if 0 <= fx < w and 0 <= fy < h:
                        cv2.circle(frame, (fx,fy), max(1,thick//3), fc, -1)

            # Droplets at tip
            if pts and self.active:
                lx, ly, la, _ = pts[-1]
                if 0 <= lx < w and 0 <= ly < h:
                    self.particles.emit(lx, ly, 3, (B, G, 20),
                                        speed=2.0, spread=50,
                                        direction=int(math.degrees(la)),
                                        lifetime=0.6, size=3)

        for i in reversed(dead):
            self._slashes.pop(i)

        self.particles.update(dt)
        self.particles.draw(frame)

        if alpha > 0.3:
            _draw_water_text(frame, alpha, self._t)

        return frame


def _draw_water_text(frame, alpha, t):
    h, w = frame.shape[:2]
    font  = cv2.FONT_HERSHEY_DUPLEX
    text  = "WATER BREATHING"
    scale = 1.4; thick = 3
    (tw,_),_ = cv2.getTextSize(text, font, scale, thick)
    x = (w-tw)//2; y = h-38
    for i, ch in enumerate(text):
        char_x = x + i * int(tw / max(1, len(text)))
        char_y = y + int(math.sin(t*4 + i*0.5) * 6)
        cv2.putText(frame, ch, (char_x-2,char_y+2), font, scale,
                    (int(200*alpha), int(80*alpha), 0), thick+3)
        cv2.putText(frame, ch, (char_x,char_y), font, scale,
                    (int(255*alpha), int(200*alpha), int(30*alpha)), thick)
