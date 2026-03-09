# 🌀 Anime Effects – Real-Time Hand Gesture FX

A real-time anime visual effects system powered by **MediaPipe** and **OpenCV**. Perform hand gestures in front of your webcam to unleash Rasengan, Chidori, and Water Breathing effects!

---


| Gesture | Effect |
|---|---|
| ✋ Right hand open | 🌀 **Rasengan** |
| 🤚 Left hand open | ⚡ **Chidori** |
| 🙌 Both hands open | 💧 **Water Breathing** |

---

## 📁 Project Structure

```
ANIME_EFFECTS/
├── effects/
│   ├── chidori.py        # Chidori lightning effect
│   ├── rasengan.py       # Rasengan swirling orb effect
│   └── water.py          # Water Breathing slash effect
├── utils/
│   ├── gestures.py       # Hand gesture detection logic
│   └── particles.py      # Particle & lightning systems
└── main.py               # Main entry point
```

---

## ⚙️ Requirements

- Python 3.8+
- Webcam

### Install Dependencies

```bash
pip install opencv-python mediapipe numpy
```

Or using a `requirements.txt`:

```bash
pip install -r requirements.txt
```

**`requirements.txt`**
```
opencv-python>=4.5.0
mediapipe>=0.10.0
numpy>=1.21.0
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/anime-effects.git
cd anime-effects
```

### 2. Install dependencies

```bash
pip install opencv-python mediapipe numpy
```

### 3. Run the app

```bash
python main.py
```

Make sure your **webcam is connected** and not being used by another application.

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `2` | Trigger Rasengan manually |
| `4` | Trigger Water Breathing manually |
| `5` | Trigger Chidori manually |
| `R` | Reset / deactivate all effects |
| `Q` | Quit |

---

## 🖐️ Gesture Guide

Gestures are detected using MediaPipe Hands. Hold the gesture for **~0.5 seconds** to activate the effect.

- **Rasengan** – Open your **right hand** (palm facing camera, all 4 fingers extended)
- **Chidori** – Open your **left hand** (palm facing camera, all 4 fingers extended)
- **Water Breathing** – Open **both hands** simultaneously (overrides single-hand effects)

---

## 🛠️ How It Works

- **MediaPipe Hands** detects and tracks hand landmarks in real-time
- **GestureDetector** (`utils/gestures.py`) classifies open-palm gestures and applies a hold-time lock (0.5s) to prevent accidental triggers
- Each effect (`effects/`) renders over the webcam frame using OpenCV drawing primitives
- **ParticleSystem** (`utils/particles.py`) uses NumPy arrays for high-performance particle simulation
- **LightningSystem** generates recursive forking lightning bolts

---

## 📦 Effect Details

### ⚡ Chidori (`effects/chidori.py`)
- Follows your **left hand** position
- Electric lightning burst + glowing aura
- Screen flicker effect

### 🌀 Rasengan (`effects/rasengan.py`)
- Follows your **right hand** position
- Spinning swirl ball with bloom glow
- Shockwave ring on activation + orbiting particles

### 💧 Water Breathing (`effects/water.py`)
- Surrounds your **full body** (uses pose landmarks)
- Animated water slash arcs with foam edges
- Blue screen tint

---

## 🤝 Contributing

Pull requests are welcome! Feel free to add new effects, improve gesture detection, or optimize performance.

1. Fork the repo
2. Create a branch: `git checkout -b feature/new-effect`
3. Commit changes: `git commit -m "Add new effect"`
4. Push: `git push origin feature/new-effect`
5. Open a Pull Request

---

## 📄 License

MIT License – feel free to use and modify.

---

> Made with ❤️ for anime fans and Python enthusiasts
