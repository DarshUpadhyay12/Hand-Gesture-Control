import numpy as np
import cv2

class DrawingController:
    def __init__(self):
        self.canvas = None
        self.color = (255, 0, 255)
        self.brush_thickness = 15
        self.eraser_thickness = 50
        self.xp, self.yp = 0, 0

    def draw(self, img, x, y, fingers):
        if self.canvas is None:
            self.canvas = np.zeros_like(img)

        # Draw Mode
        if fingers[1] and not fingers[2]:
            if self.xp == 0 and self.yp == 0:
                self.xp, self.yp = x, y
            
            cv2.line(self.canvas, (self.xp, self.yp), (x, y), self.color, self.brush_thickness)
            cv2.line(img, (self.xp, self.yp), (x, y), self.color, self.brush_thickness)
            self.xp, self.yp = x, y

        # Erase Mode
        elif fingers[1] and fingers[2]:
            self.xp, self.yp = 0, 0
            cv2.circle(img, (x, y), self.eraser_thickness, (0, 0, 0), cv2.FILLED)
            cv2.circle(self.canvas, (x, y), self.eraser_thickness, (0, 0, 0), cv2.FILLED)

        else:
            self.xp, self.yp = 0, 0

        # Combine
        img_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, self.canvas)
        
        return img

    def clear(self):
        if self.canvas is not None:
            self.canvas = np.zeros_like(self.canvas)
