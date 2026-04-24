import rclpy
import cv2
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped


from ros2_project_el23st.camera_subscriber import CameraSubscriber
from ros2_project_el23st.colour_mask import ColourMask
from ros2_project_el23st.object_detector import ObjectDetector
from ros2_project_el23st.robot_controller import RobotController

class ProjectMain(Node):
    def __init__(self):
        super().__init__('project_main')
        
        # initialise functions
        self.camera = CameraSubscriber()
        self.masker = ColourMask()
        self.detector = ObjectDetector()
        self.robot = RobotController()
        
        
        self.get_logger().info("Project Started")
    
    def run(self):
        # ---main---
        while rclpy.ok():
            rclpy.spin_once(self.camera, timeout_sec=0.1)
            rclpy.spin_once(self.robot, timeout_sec=0.1)
            rclpy.spin_once(self.robot.goal_client, timeout_sec=0.1)
            
            # get image
            frame = self.camera.get_image()
            if frame is None:
                continue
            
            # build all 3 masks
            blue_mask = self.masker.get_blue_mask(frame)
            red_mask = self.masker.get_red_mask(frame)
            green_mask = self.masker.get_green_mask(frame)
            
            # blue colour detections
            detected_blue, area, center, bbox = self.detector.detect_blue(blue_mask, frame)
                     
            # show all image
            cv2.imshow('Camera Feed', frame)
            cv2.imshow('Blue Mask', blue_mask)
            cv2.imshow('Red Mask', red_mask)
            cv2.imshow('Green Mask', green_mask)
            
            key = cv2.waitKey(3) & 0xFF
            if key == ord('q'):
                break
            
            # --- core logic ---
            '''
            if not self.started_explore:
                if self.robot.current_wp < len(self.robot.waypoints):
                    self.robot.explore()
                self.started_explore = True
                #continue
            '''
            if self.robot.state == 'EXPLORE':
                # Navigation is handled automatically by a timer within the RobotController; 
                # here, only the blue area is recorded.
                if detected_blue and not self.robot.blue_found:
                    self.robot.blue_found = True
                    self.get_logger().info("Blue detected during exploration, will approach later")
            
            elif self.robot.state == 'APPROACH':
                if detected_blue:
                    if self.detector.is_close_enough(threshold=50000):
                        self.robot.stop()
                        self.get_logger().info("Misson complete")
                        break
                    else:
                        twist =  Twist()
                        twist.angular.z = 0.2
                        self.robot.cmd_pub.publish(twist)
            
        cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    project = ProjectMain()
    try:
        project.run()
    except KeyboardInterrupt:
        project.get_logger().info("Shutting down...")
    finally:
        project.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()