import cv2
import numpy as np

class ObjectDetector:
    def __init__(self):
        self.blue_detected = False
        self.blue_area = 0
        self.blue_center = (0, 0)
        self.blue_bbox = None
        
    def detect_blue(self, blue_mask, original_image):
        """detecting blue, return have/haven't detected, area, centre and boundary"""
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            self.blue_detected = False
            self.blue_area = 0
            return False, 0, (0, 0), None
        
        # find Max Boundary 
        largest = max(contours, key=cv2.contourArea)
        self.blue_area = cv2.contourArea(largest)
        
        # calculate centre
        M = cv2.moments(largest)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            self.blue_center = (cx, cy)
        else:
            self.blue_center = (320, 240)
        
        # get boundary (for display)
        x, y, w, h = cv2.boundingRect(largest)
        self.blue_bbox = (x, y, w, h)
        
        # draw frames on images
        cv2.rectangle(original_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.circle(original_image, (cx, cy), 5, (0, 0, 255), -1)
        
        self.blue_detected = True
        return True, self.blue_area, self.blue_center, self.blue_bbox
    
    def is_close_enough(self, threshold=50000):
        """close evnough?"""
        return self.blue_area > threshold