====================================================================
  🦖 MotionDino — Webcam-Based Gesture Controlled Dino Game 📸
====================================================================

MotionDino is a real-time endless runner game inspired by Chrome's 
classic Dino game. Instead of keyboard controls, players control 
the Dino using full-body motion detected via a webcam.

The application combines Computer Vision (CV), Human-Computer 
Interaction (HCI), and 2D Game Engine Development into a lightweight 
desktop experience optimized for normal laptop hardware.


--------------------------------------------------------------------
  🌟 FEATURES
--------------------------------------------------------------------

* 🎯 Real-Time Pose Detection: Tracks body landmarks at low latency.
* 📏 Dynamic Calibration: Calculates jump thresholds based on your 
  height and camera distance instead of hardcoded pixel values.
* ⚡ Debouncing & Smoothing: Eliminates false jump triggers using 
  moving averages and cooldown timers.
* 📹 Live Camera Preview: Shows skeletal landmarks and action state 
  in the top-right corner.
* ⌨️ Keyboard Fallback: Plays via SPACE / UP key if no camera is 
  available.


--------------------------------------------------------------------
  🛠️ TECH STACK
--------------------------------------------------------------------

* 🐍 Python 3.10+   : Core programming language
* 🎮 Pygame         : Game engine, physics, and rendering
* 👁️ OpenCV         : Video capture and camera overlay
* 🤖 MediaPipe      : Real-time body pose landmark tracking
* 🔢 NumPy          : Moving average math calculations


--------------------------------------------------------------------
  🔄 HOW THE PIPELINE WORKS
--------------------------------------------------------------------

📹 Webcam Frame
      │
      ▼
👁️ OpenCV (Resize & Flip)
      │
      ▼
🤖 MediaPipe Pose (Extract Hip/Shoulder Landmarks)
      │
      ▼
⚡ Gesture Detector (Compare Smoothed Y Position to Calibration)
      │
      ▼
🎯 Jump Event Triggered
      │
      ▼
🦖 Pygame Dino Jump Physics


--------------------------------------------------------------------
  📂 PROJECT STRUCTURE
--------------------------------------------------------------------

motion-dino/
├── main.py                 # 🚀 Main entry point
├── requirements.txt        # 📦 Dependencies
├── README.md               # 📜 Documentation
│
├── game/
│   ├── __init__.py
│   ├── settings.py         # ⚙️ Physics and screen settings
│   ├── dino.py             # 🦖 Dino player logic
│   ├── obstacle.py         # 🌵 Obstacle spawning & movement
│   └── engine.py           # 🕹️ Game engine & UI rendering
│
└── vision/
    ├── __init__.py
    ├── camera.py           # 📹 Camera handling
    └── gesture.py          # 🎯 Pose detection & calibration


--------------------------------------------------------------------
  🚀 INSTALLATION & SETUP
--------------------------------------------------------------------

1. Clone the repository:
   git clone https://github.com/your-username/motion-dino.git
   cd motion-dino

2. Create and activate a virtual environment:

   Windows:
   python -m venv venv
   venv\Scripts\activate

   Mac/Linux:
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run the application:
   python main.py


--------------------------------------------------------------------
  🎮 HOW TO PLAY
--------------------------------------------------------------------

1. 💻 Run python main.py.
2. ⌨️ Press SPACE or ENTER on the start screen.
3. 🧍 Stand 1–2 meters back from your camera.
4. ⏱️ Stand still for 1 second during CALIBRATION.
5. 🦘 Jump in real life to make the Dino jump over cacti!
6. ❌ Press ESC at any time to exit.