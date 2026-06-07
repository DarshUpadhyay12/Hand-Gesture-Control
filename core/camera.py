import cv2
import threading
import time
from loguru import logger

class Camera:
    def __init__(self, config):
        self.config = config
        self.cam_index = self.config.get("general", "camera_index")
        self.width = self.config.get("general", "width")
        self.height = self.config.get("general", "height")
        self.fps = self.config.get("general", "fps")
        self.cap = None
        self.running = False
        self.frame = None
        self.lock = threading.Lock()

    def start(self):
        self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            logger.warning(f"Failed to open camera index {self.cam_index} with CAP_DSHOW, trying default...")
            self.cap = cv2.VideoCapture(self.cam_index)
            
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera index {self.cam_index} completely.")
            return
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.running = True
        threading.Thread(target=self._update, daemon=True).start()
        logger.info("Camera started.")

    def _update(self):
        while self.running:
            success, frame = self.cap.read()
            if success:
                frame = cv2.flip(frame, 1)  # Mirror
                with self.lock:
                    self.frame = frame
            else:
                logger.error("Failed to read frame from camera.")
                time.sleep(1)

    def get_frame(self):
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
            return None

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        logger.info("Camera stopped.")
