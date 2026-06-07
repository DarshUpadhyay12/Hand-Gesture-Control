import pyautogui
import numpy as np
from pynput.mouse import Controller, Button
from loguru import logger

class MouseController:
    def __init__(self, config):
        self.config = config
        self.screen_w, self.screen_h = pyautogui.size()
        self.mouse = Controller()
        
        self.frame_r = 100 # Frame reduction
        self.smoothness = self.config.get("sensitivity", "mouse_smoothness")
        self.pinch_threshold = self.config.get("sensitivity", "pinch_threshold")
        self.scroll_speed = self.config.get("sensitivity", "scroll_speed")
        
        self.ploc_x, self.ploc_y = 0, 0
        self.cloc_x, self.cloc_y = 0, 0
        
        pyautogui.FAILSAFE = False

    def move(self, x, y, frame_w, frame_h):
        # Convert coordinates
        x3 = np.interp(x, (self.frame_r, frame_w - self.frame_r), (0, self.screen_w))
        y3 = np.interp(y, (self.frame_r, frame_h - self.frame_r), (0, self.screen_h))
        
        # Smooth values
        self.cloc_x = self.ploc_x + (x3 - self.ploc_x) / self.smoothness
        self.cloc_y = self.ploc_y + (y3 - self.ploc_y) / self.smoothness
        
        try:
            self.mouse.position = (self.cloc_x, self.cloc_y)
        except Exception as e:
            pass
            
        self.ploc_x, self.ploc_y = self.cloc_x, self.cloc_y

    def left_click(self):
        self.mouse.click(Button.left, 1)

    def right_click(self):
        self.mouse.click(Button.right, 1)

    def double_click(self):
        self.mouse.click(Button.left, 2)

    def drag(self, start=True):
        if start:
            self.mouse.press(Button.left)
        else:
            self.mouse.release(Button.left)
            
    def scroll(self, direction="up"):
        if direction == "up":
            self.mouse.scroll(0, 1)
        else:
            self.mouse.scroll(0, -1)
