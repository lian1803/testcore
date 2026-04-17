# Hand-Controlled 3D Particle System

An interactive 3D particle system controlled by hand gestures using MediaPipe Hands and Three.js. Move your hands in front of your webcam to interact with 15,000+ particles in real-time!

![Particle System](https://img.shields.io/badge/particles-15000-blue)
![Tech](https://img.shields.io/badge/tech-three.js-green)
![Tracking](https://img.shields.io/badge/tracking-MediaPipe-orange)

## Features

### 🎮 Hand Gestures
- **One Hand**: Push particles away from your palm
- **Two Hands Together**: Attract particles to the center point between your hands (magnetic effect)
- **Spread Hands**: Each hand independently repels particles

### ✨ Visual Effects
- 15,000 particles with gradient colors
- Real-time physics simulation
- Smooth hand tracking with palm-center detection
- Visual feedback for gesture recognition
- Glassmorphic UI design

### 🎛️ Interactive Controls
- Adjust particle count (1,000 - 50,000)
- Control particle size
- Modify animation speed
- Adjust hand influence strength
- Pause/Resume animation
- Camera controls (zoom, rotate)

## Technologies Used

- **Three.js** - 3D graphics and particle rendering
- **MediaPipe Hands** - Real-time hand tracking
- **WebGL** - Hardware-accelerated rendering
- **ES6 Modules** - Modern JavaScript

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Edge, or Firefox recommended)
- Webcam access
- Good lighting for hand tracking

### Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd particle-system
```

2. Open `index.html` in your browser:
```bash
# On Windows
start index.html

# Or just double-click the file
```

3. Allow camera access when prompted

4. Show your hand(s) in front of the camera and start interacting!

## How to Use

1. **Single Hand Mode**: 
   - Hold one hand in front of the camera
   - Move it around to push particles away
   - The particles will flee from your palm

2. **Attraction Mode**: 
   - Show both hands
   - Bring them close together (within ~30cm)
   - Watch particles concentrate at the center point
   - A red indicator will appear confirming attraction mode

3. **Controls**:
   - **Scroll**: Zoom in/out
   - **Click & Drag**: Rotate camera view
   - **Sliders**: Adjust particle properties in real-time

## Technical Details

### Hand Tracking
- Uses MediaPipe Hands for ML-based hand detection
- Tracks palm center (average of 5 key landmarks)
- Supports up to 2 hands simultaneously
- Inverted X-axis for natural interaction

### Particle Physics
- Repulsion force in normal mode
- Attraction force when hands are close
- Velocity damping for smooth motion
- Return-to-origin spring force
- 3D coordinate mapping from 2D hand position

### Performance
- Optimized for 15,000 particles
- Uses BufferGeometry for efficient rendering
- Additive blending for glow effects
- Real-time position updates at 60 FPS

## Customization

Edit the JavaScript constants in `index.html`:

```javascript
let particleCount = 15000;  // Number of particles
let particleSize = 2.5;      // Size of each particle
let speed = 1.2;             // Animation speed
let handInfluence = 12;      // Force strength
```

## Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari (with WebRTC support)
- ❌ Internet Explorer (not supported)

## License

MIT License - Feel free to use and modify!

## Credits

Created with:
- [Three.js](https://threejs.org/)
- [MediaPipe](https://mediapipe.dev/)
- Hand gesture detection powered by Google's ML models

---

**Enjoy interacting with particles! 🎨✨**
