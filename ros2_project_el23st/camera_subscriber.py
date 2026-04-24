import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        
        #CvBridge created
        self.bridge = CvBridge()
        
        #subscriber
        self.subscription = self.create_subscription(
            Image, 
            '/camera/image_raw',
            self.callback,
            10
        )
        self.latest_image = None
        
    def callback(self, data):
        """Convert ROS Image message to a BGR OpenCV image"""
        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(data, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'CvBridge Error: {e}')
    
    def get_image(self):
        """take latest image for other functions"""
        return self.latest_image