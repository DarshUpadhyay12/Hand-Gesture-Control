import cv2
import mediapipe as mp
import math
import os
import urllib.request
from loguru import logger
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_con=0.8, track_con=0.8):
        self.max_hands = max_hands
        self.tip_ids = [4, 8, 12, 16, 20]
        
        self.model_path = 'hand_landmarker.task'
        if not os.path.exists(self.model_path):
            logger.info("Downloading hand_landmarker.task...")
            urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', self.model_path)
            logger.info("Download complete.")
            
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.max_hands,
            min_hand_detection_confidence=float(detection_con),
            min_hand_presence_confidence=float(track_con),
            min_tracking_confidence=float(track_con)
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.detection_result = None

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        self.detection_result = self.detector.detect(mp_image)
        
        if self.detection_result.hand_landmarks:
            for hand_landmarks in self.detection_result.hand_landmarks:
                if draw:
                    h, w, c = img.shape
                    # Draw connections
                    for connection in HAND_CONNECTIONS:
                        x0, y0 = int(hand_landmarks[connection[0]].x * w), int(hand_landmarks[connection[0]].y * h)
                        x1, y1 = int(hand_landmarks[connection[1]].x * w), int(hand_landmarks[connection[1]].y * h)
                        cv2.line(img, (x0, y0), (x1, y1), (0, 255, 0), 2)
                    # Draw landmarks
                    for lm in hand_landmarks:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        cv2.circle(img, (cx, cy), 3, (0, 0, 255), cv2.FILLED)
        return img

    def get_all_hands_info(self, img):
        hands_info = []
        if self.detection_result and self.detection_result.hand_landmarks:
            h, w, c = img.shape
            for idx, hand_landmarks in enumerate(self.detection_result.hand_landmarks):
                lm_list = []
                for id, lm in enumerate(hand_landmarks):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
                
                fingers = self.fingers_up(lm_list)
                
                # MediaPipe handedness is based on the image as-is. Since we flip the image horizontally in camera, 
                # what MediaPipe thinks is Left is actually the user's Right hand.
                handedness = self.detection_result.handedness[idx][0].category_name
                if handedness == "Left":
                    handedness = "Right"
                elif handedness == "Right":
                    handedness = "Left"
                    
                hands_info.append({
                    "lm_list": lm_list,
                    "fingers": fingers,
                    "handedness": handedness
                })
        return hands_info

    def fingers_up(self, lm_list):
        fingers = []
        if len(lm_list) != 0:
            def dist(p1, p2):
                return math.hypot(lm_list[p1][1] - lm_list[p2][1], lm_list[p1][2] - lm_list[p2][2])
                
            # Thumb: measure distance to pinky base (17)
            if dist(4, 17) > dist(3, 17):
                fingers.append(1)
            else:
                fingers.append(0)
            
            # Other 4 fingers: measure distance to wrist (0)
            for id in range(1, 5):
                tip_id = self.tip_ids[id]
                pip_id = tip_id - 2
                if dist(tip_id, 0) > dist(pip_id, 0):
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers

    def find_distance(self, p1, p2, lm_list, img, draw=True, r=15, t=3):
        x1, y1 = lm_list[p1][1], lm_list[p1][2]
        x2, y2 = lm_list[p2][1], lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
            
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]
