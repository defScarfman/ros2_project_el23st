# Exercise 1 - Display an image of the camera feed to the screen

#from __future__ import division
import threading
import sys, time
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from rclpy.exceptions import ROSInterruptException
import signal


class colourIdentifier(Node):
    def __init__(self):
        super().__init__('cI')
        
        #CvBridge created
        self.bridge = CvBridge() 
        # Remember to initialise a CvBridge() and set up a subscriber to the image topic you wish to use
        # We covered which topic to subscribe to should you wish to receive image data

        #subscriber
        self.subscription = self.create_subscription(
            Image,
            'camera/image_raw',
            self.callback,
            10
        )
        
        self.subscription  # prevent unused variable warning
        self.get_logger().info('Subscribed to camera/image_raw')
        
    def callback(self, msg: Image):
        """receive iamge messages and display them with oencv."""
        try:
            
# Convert ROS Image message to a BGR OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Show the image
            cv2.imshow('Camera Feed (RGB)', cv_image)
            # waitKey is required for imshow to update; small delay is fine
            cv2.waitKey(1)

        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge Error: {e}')
        except Exception as e:
            self.get_logger().error(f'Unexpected error in callback: {e}')
        #return
        # Convert the received image into a opencv image
        # But remember that you should always wrap a call to this conversion method in an exception handler
        # Show the resultant images you have created.
        

# Create a node of your class in the main and ensure it stays up and running
# handling exceptions and such
def main():

    def signal_handler(sig, frame):
        rclpy.shutdown()
    # Instantiate your class
    # And rclpy.init the entire node
    rclpy.init(args=None)
    cI = colourIdentifier()


    signal.signal(signal.SIGINT, signal_handler)
    thread = threading.Thread(target=rclpy.spin, args=(cI,), daemon=True)
    thread.start()

    try:
        while rclpy.ok():
            continue
    except ROSInterruptException:
        pass

    # Remember to destroy all image windows before closing node
    cv2.destroyAllWindows()
    

# Check if the node is executing in the main path
if __name__ == '__main__':
    main()
