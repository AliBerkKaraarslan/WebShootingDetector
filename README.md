# Spider-Man Web-Shooting Gesture Detector
Python-based project that uses computer vision techniques to detect Spider-Man's iconic web-shooting gesture. This system can recognize the specific motion used by Spider-Man when he shoots his webs.

## How It Works
The program uses [Google's MediaPipe Hand Landmark model](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker), which detects 21 key landmarks (joints) of the hand in real-time from a video feed.

Once the hand is detected, the program calculates the distances between specific hand joints.

The program compares the distances between these joints and uses predefined thresholds to determine if the hand is performing the web-shooting motion.

Once the gesture is detected, the program provides visual and auditory feedback to indicate successful recognition. The feedback can be seen directly on the video feed.

## How to Run

Run the following command on command prompt:
```bash
python3 src/webshooter_detection.py
```

##

Ali Berk Karaarslan
##

2024
