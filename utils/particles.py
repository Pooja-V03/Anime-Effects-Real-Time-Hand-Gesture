
import numpy as np
import cv2


class ParticleSystem:
    def __init__(self, max_particles=300):
        self.max_particles = max_particles
        self.reset()

    def reset(self):
        self.positions  = np.zeros((self.max_particles, 2), dtype=np.float32)
        self.velocities = np.zeros((self.max_particles, 2), dtype=np.float32)
        self.lifetimes  = np.zeros(self.max_particles, dtype=np.float32)
        self.max_life   = np.ones(self.max_particles,  dtype=np.float32)
        self.colors     = np.zeros((self.max_particles, 3), dtype=np.uint8)
        self.sizes      = np.ones(self.max_particles,  dtype=np.float32) * 3
        self.active     = np.zeros(self.max_particles, dtype=bool)

    def emit(self, x, y, count, color, speed=2.0, spread=360,
             direction=270, lifetime=1.0, size=3):
        dead = np.where(~self.active)[0]
        count = min(count, len(dead))
        if count == 0:
            return
        idx = dead[:count]
        angles = np.radians(
            direction + (np.random.rand(count) - 0.5) * spread
        )
        speeds = speed * (0.5 + np.random.rand(count))
        self.positions[idx]  = [x, y]
        self.velocities[idx] = np.stack([np.cos(angles)*speeds,
                                          np.sin(angles)*speeds], axis=1)
        self.lifetimes[idx]  = lifetime * (0.7 + 0.3*np.random.rand(count))
        self.max_life[idx]   = self.lifetimes[idx]
        self.colors[idx]     = color
        self.sizes[idx]      = size * (0.5 + 0.5*np.random.rand(count))
        self.active[idx]     = True

    def update(self, dt=0.033):
        if not np.any(self.active):
            return
        a = self.active
        self.positions[a]  += self.velocities[a] * dt * 30
        self.lifetimes[a]  -= dt
        self.active[a]      = self.lifetimes[a] > 0

    def draw(self, frame):
        h, w = frame.shape[:2]
        for i in np.where(self.active)[0]:
            x, y = int(self.positions[i, 0]), int(self.positions[i, 1])
            if 0 <= x < w and 0 <= y < h:
                alpha = max(0.0, self.lifetimes[i] / self.max_life[i])
                c = (int(self.colors[i,0]*alpha),
                     int(self.colors[i,1]*alpha),
                     int(self.colors[i,2]*alpha))
                r = max(1, int(self.sizes[i] * alpha))
                cv2.circle(frame, (x, y), r, c, -1)


class LightningSystem:
    """Forking lightning bolt renderer."""

    @staticmethod
    def draw_bolt(frame, x1, y1, x2, y2, color=(255,255,255),
                  thickness=2, roughness=0.4, depth=4):
        if depth == 0 or ((x2-x1)**2+(y2-y1)**2) < 25:
            cv2.line(frame, (int(x1),int(y1)), (int(x2),int(y2)), color, thickness)
            return
        mx = (x1+x2)/2 + (np.random.rand()-0.5)*roughness * abs(y2-y1)
        my = (y1+y2)/2 + (np.random.rand()-0.5)*roughness * abs(x2-x1)
        LightningSystem.draw_bolt(frame, x1, y1, mx, my, color, thickness, roughness, depth-1)
        LightningSystem.draw_bolt(frame, mx, my, x2, y2, color, thickness, roughness, depth-1)
        # random branch
        if np.random.rand() < 0.4 and depth > 1:
            bx = mx + (np.random.rand()-0.5)*80
            by = my + (np.random.rand()-0.5)*80
            LightningSystem.draw_bolt(frame, mx, my, bx, by, color,
                                       max(1, thickness-1), roughness, depth-2)

    @staticmethod
    def draw_burst(frame, cx, cy, count=6, radius=80, color=(200,220,255)):
        angles = np.linspace(0, 2*np.pi, count, endpoint=False)
        angles += np.random.rand() * np.pi
        for a in angles:
            ex = cx + np.cos(a) * radius * (0.6 + 0.4*np.random.rand())
            ey = cy + np.sin(a) * radius * (0.6 + 0.4*np.random.rand())
            LightningSystem.draw_bolt(frame, cx, cy, ex, ey, color, 2)
