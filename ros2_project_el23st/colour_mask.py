import cv2
import numpy as np

class ColourMask:
    def __init__(self):
        # HSV range (need to test it)
        # red
        self.red_lower1 = np.array([0, 100, 100])
        self.red_upper1 = np.array([10, 255, 255])
        self.red_lower2 = np.array([170, 100, 100])
        self.red_upper2 = np.array([180, 255, 255])
        
        # green
        self.green_lower = np.array([40, 100, 100])
        self.green_upper = np.array([80, 255, 255])
        
        # blue
        self.blue_lower = np.array([100, 100, 100])
        self.blue_upper = np.array([130, 255, 255])
    
    def get_blue_mask(self, bgr_image):
        
        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv, self.blue_lower, self.blue_upper)
    
    def get_red_mask(self, bgr_image):
        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, self.red_lower1, self.red_upper1)
        mask2 = cv2.inRange(hsv, self.red_lower2, self.red_upper2)
        return cv2.bitwise_or(mask1, mask2)
    
    def get_green_mask(self, bgr_image):
        hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv, self.green_lower, self.green_upper)