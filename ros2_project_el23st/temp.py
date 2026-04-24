import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from ros2_project_el23st.go_to_specific_point_on_map import GoToPose
import time

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.navigator = BasicNavigator()
        #self.goal_client = GoToPose()
        self.navigator.waitUntilNav2Active()
        
        # way points
        self.waypoints = [
            (0.0, 0.0),
            (2.5, -6.5),
            (-2.7, -10.0),
            (-6.6, -2.4),
        ]
        self.current_wp = 0
        
    def start_navigation(self):
        """非阻塞方式：发送当前航点目标，立即返回"""
        if self.current_wp >= len(self.waypoints):
            self.get_logger().info("No more waypoints")
            return False

        goal_x, goal_y = self.waypoints[self.current_wp]
        self.get_logger().info(f"Starting navigation to {self.current_wp}: ({goal_x}, {goal_y})")

        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = goal_x
        goal_pose.pose.position.y = goal_y
        goal_pose.pose.orientation.w = 1.0

        self.navigator.goToPose(goal_pose)
        return True

    def is_navigation_complete(self):
        """检查当前导航是否完成（成功或失败），并处理结果"""
        if not self.navigator.isTaskComplete():
            return False
        
        self.get_logger().info(f"Navigation finished for waypoint {self.current_wp}")
        self.current_wp += 1
        return True

    def cancel_navigation(self):
        """取消当前导航任务"""
        self.navigator.cancelTask()
        self.get_logger().info("Navigation cancelled")

    def approach_blue(self, blue_center_x, blue_area, image_center=320):
        """use cmd_vel get close to blue"""
        twist = Twist()
        
        # turn first
        error = blue_center_x - image_center
        twist.angular.z = -error * 0.005
        
        # speed set up defined by area
        if blue_area < 10000:
            twist.linear.x = 0.3
        elif blue_area < 30000:
            twist.linear.x = 0.2
        else:
            twist.linear.x = 0.1
        
        self.cmd_pub.publish(twist)
    
    def stop(self):
        """stop robot"""
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)
    