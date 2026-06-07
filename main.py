import sys
import time
import cv2
import math
import traceback
from loguru import logger
from core.config import ConfigManager
from core.camera import Camera
from core.detector import HandDetector
from controllers.mouse import MouseController
from controllers.system_ops import SystemController
from controllers.media import MediaController
from controllers.presentation import PresentationController
from controllers.drawing import DrawingController
from ui.app_window import AppWindow

logger.add("app.log", rotation="1 MB")

class AppCore:
    def __init__(self):
        self.config = ConfigManager()
        self.camera = Camera(self.config)
        self.detector = HandDetector()
        
        self.mouse = MouseController(self.config)
        self.system = SystemController()
        self.media = MediaController()
        self.presentation = PresentationController()
        self.drawing = DrawingController()
        
        self.current_mode = "general"
        self.running = False
        self.processed_frame = None
        self.current_fps = 0
        self.current_gesture = "None"
        
        self.pTime = 0

    def start(self):
        self.camera.start()
        self.running = True
        import threading
        threading.Thread(target=self.process_loop, daemon=True).start()
        
        app = AppWindow(self)
        app.mainloop()

    def stop(self):
        self.running = False
        self.camera.stop()
        logger.info("Application stopped.")

    def get_processed_frame(self):
        return self.processed_frame

    def process_loop(self):
        while self.running:
            try:
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue

                frame = self.detector.find_hands(frame)
                hands_info = self.detector.get_all_hands_info(frame)
                
                h, w, c = frame.shape
                
                self.current_gesture = "None"
                
                left_hand = None
                right_hand = None

                for hand in hands_info:
                    if hand["handedness"] == "Left":
                        left_hand = hand
                    else:
                        right_hand = hand

                # GLOBAL GESTURES
                global_gesture_triggered = False

                if left_hand and right_hand:
                    left_fingers = left_hand["fingers"]
                    right_fingers = right_hand["fingers"]
                    left_wrist = left_hand["lm_list"][0]
                    right_wrist = right_hand["lm_list"][0]
                    dist_wrists = math.hypot(left_wrist[1]-right_wrist[1], left_wrist[2]-right_wrist[2])

                    # 1. 🙏 Prayer Gesture (Close Everything)
                    if dist_wrists < 100 and all(f == 1 for f in left_fingers) and all(f == 1 for f in right_fingers):
                        self.request_close_all = True
                        self.current_gesture = "Close Everything"
                        time.sleep(2.0)
                        global_gesture_triggered = True

                    # 2. 👏 Clap Gesture (Open Brave + ChatGPT)
                    elif dist_wrists < 60 and not all(f == 1 for f in left_fingers) and not all(f == 0 for f in left_fingers):
                        self.system.open_brave_chatgpt()
                        self.current_gesture = "Open ChatGPT"
                        time.sleep(2.0)
                        global_gesture_triggered = True

                if not global_gesture_triggered and left_hand:
                    fingers = left_hand["fingers"]
                    lm_list = left_hand["lm_list"]
                    
                    # 3. 👌 OK Gesture (Alt + Tab)
                    dist_ok = math.hypot(lm_list[4][1]-lm_list[8][1], lm_list[4][2]-lm_list[8][2])
                    if dist_ok < 40 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
                        self.system.alt_tab()
                        self.current_gesture = "Alt + Tab"
                        time.sleep(0.5)
                        global_gesture_triggered = True
                        
                    # 4. ✌️ Victory (Open YouTube)
                    elif fingers == [0, 1, 1, 0, 0]:
                        self.system.open_youtube()
                        self.current_gesture = "Open YouTube"
                        time.sleep(1.0)
                        global_gesture_triggered = True
                        
                    # 5. Three Fingers (Open File Manager)
                    elif fingers == [0, 1, 1, 1, 0]:
                        self.system.open_file_manager()
                        self.current_gesture = "Open File Explorer"
                        time.sleep(1.0)
                        global_gesture_triggered = True
                        
                    # 6. Four Fingers (Windows + H)
                    elif fingers == [0, 1, 1, 1, 1]:
                        self.system.open_win_h()
                        self.current_gesture = "Win + H"
                        time.sleep(1.0)
                        global_gesture_triggered = True
                        
                    # 7. 👍 Thumbs Up (Minimize All Apps)
                    elif fingers == [1, 0, 0, 0, 0]:
                        tip_y4 = lm_list[4][2]
                        mcp_y4 = lm_list[3][2]
                        if tip_y4 < mcp_y4 - 10:
                            self.system.show_desktop()
                            self.current_gesture = "Minimize All Apps"
                            time.sleep(1.0)
                            global_gesture_triggered = True
                            
                    # 8. 🤘 Rock Gesture (Open Cricbuzz)
                    elif fingers == [0, 1, 0, 0, 1]:
                        self.system.open_cricbuzz()
                        self.current_gesture = "Open Cricbuzz"
                        time.sleep(1.0)
                        global_gesture_triggered = True
                        
                    # 9. 🤙 Call Me (Open Streaming)
                    elif fingers == [1, 0, 0, 0, 1]:
                        self.system.open_streaming()
                        self.current_gesture = "Open Streaming"
                        time.sleep(1.0)
                        global_gesture_triggered = True

                if not global_gesture_triggered:
                    if self.current_mode == "mouse":
                        hand = right_hand if right_hand else left_hand
                        if hand:
                            fingers = hand["fingers"]
                            lm_list = hand["lm_list"]
                            x1, y1 = lm_list[8][1:]
                            
                            if fingers == [0, 1, 0, 0, 0]:
                                self.mouse.move(x1, y1, w, h)
                                cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                                self.current_gesture = "Mouse Moving"
                            elif fingers == [0, 1, 1, 0, 0]:
                                length, frame, lineInfo = self.detector.find_distance(8, 12, lm_list, frame)
                                if length < self.mouse.pinch_threshold:
                                    cv2.circle(frame, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                                    self.mouse.left_click()
                                    self.current_gesture = "Left Click"
                                    time.sleep(0.2)
                            elif fingers == [1, 0, 1, 0, 0]:
                                length, frame, lineInfo = self.detector.find_distance(4, 12, lm_list, frame)
                                if length < self.mouse.pinch_threshold:
                                    self.mouse.right_click()
                                    self.current_gesture = "Right Click"
                                    time.sleep(0.3)
                            elif fingers == [1, 1, 0, 0, 0]:
                                length, frame, lineInfo = self.detector.find_distance(4, 8, lm_list, frame)
                                self.system.set_volume(length)
                                self.current_gesture = "Volume Control"

                    elif self.current_mode == "media":
                        hand = left_hand if left_hand else right_hand
                        if hand:
                            fingers = hand["fingers"]
                            lm_list = hand["lm_list"]
                            x1, y1 = lm_list[8][1:]
                            
                            if all(f == 1 for f in fingers):
                                self.media.play_pause()
                                self.current_gesture = "Play/Pause"
                                time.sleep(0.5)
                            elif all(f == 0 for f in fingers):
                                self.media.mute()
                                self.current_gesture = "Mute"
                                time.sleep(0.5)
                            elif fingers == [0, 1, 0, 0, 0]:
                                tip_x = lm_list[8][1]
                                mcp_x = lm_list[5][1]
                                
                                if tip_x > mcp_x + 30:  # Pointing Right
                                    self.media.skip_forward()
                                    self.current_gesture = "Skip Forward (Right)"
                                    time.sleep(0.5)
                                elif tip_x < mcp_x - 30:  # Pointing Left
                                    self.media.skip_backward()
                                    self.current_gesture = "Skip Backward (Left)"
                                    time.sleep(0.5)
                                else:
                                    self.current_gesture = "Media Ready"

                    elif self.current_mode == "presentation":
                        hand = right_hand if right_hand else left_hand
                        if hand:
                            fingers = hand["fingers"]
                            lm_list = hand["lm_list"]
                            x1, y1 = lm_list[8][1:]
                            
                            if fingers == [0, 1, 0, 0, 0]:
                                tip_y = lm_list[8][2]
                                mcp_y = lm_list[5][2]
                                
                                if tip_y > mcp_y + 20:  # Pointing Downwards (Y increases downwards)
                                    self.presentation.next_slide()
                                    self.current_gesture = "Next Slide (Down)"
                                    time.sleep(0.5)
                                elif tip_y < mcp_y - 20:  # Pointing Upwards
                                    self.presentation.prev_slide()
                                    self.current_gesture = "Prev Slide (Up)"
                                    time.sleep(0.5)
                                else:
                                    self.current_gesture = "Pointer Ready"

                    elif self.current_mode == "drawing":
                        # Use right hand for drawing preferably, or left if right not found
                        hand_to_draw = right_hand if right_hand else left_hand
                        if hand_to_draw:
                            fingers = hand_to_draw["fingers"]
                            lm_list = hand_to_draw["lm_list"]
                            x1, y1 = lm_list[8][1:]
                            
                            frame = self.drawing.draw(frame, x1, y1, fingers)
                            if all(f == 0 for f in fingers): # clear
                                self.drawing.clear()
                                self.current_gesture = "Clear Canvas"

                # FPS Calculation
                cTime = time.time()
                self.current_fps = 1 / (cTime - self.pTime) if (cTime - self.pTime) > 0 else 0
                self.pTime = cTime

                self.processed_frame = frame
                time.sleep(0.01)

            except Exception as e:
                logger.error(f"Error in process loop: {e}")
                logger.debug(traceback.format_exc())
                time.sleep(0.1)

if __name__ == "__main__":
    app = AppCore()
    app.start()
