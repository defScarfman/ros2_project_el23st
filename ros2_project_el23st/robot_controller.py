import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
#from nav2_simple_commander.robot_navigator import BasicNavigator
from ros2_project_el23st.go_to_specific_point_on_map import GoToPose
import time

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.goal_client = GoToPose()
        
        self.get_logger().info("Waiting for navigate_to_pose action server...")
        self.goal_client.action_client.wait_for_server()
        self.get_logger().info("Action server ready")
        # way points
        self.waypoints = [
            (2.5, -6.5),
            (-2.7, -10.0),
            (-6.6, -2.4),
            (0.0, 0.0),
        ]
        self.current_wp = 0
        # explore state
        self.state = 'EXPLORE'
        self.blue_records = []
        self.blue_found = False
        # timer
        self.timer = self.create_timer(0.1, self._navigation_state_machine)
        self.navigation_in_progress = False

    def _navigation_state_machine(self):
        if self.state == 'EXPLORE':
            if not self.navigation_in_progress:
                if self.current_wp < len(self.waypoints):
                    x, y = self.waypoints[self.current_wp]
                    self.get_logger().info(f"Start navigating to wp {self.current_wp}: ({x}, {y})")
                    self.goal_client.send_goal_nonblocking(x, y)
                    self.navigation_in_progress = True
                else:
                    self.state = 'APPROACH'
                    self.get_logger().info("Exploration finished, switching to APPROACH")
            else:
                # 检查导航是否完成
                if self.goal_client.is_goal_finished():
                    if self.goal_client.is_goal_successful():
                        self.get_logger().info(f"Waypoint {self.current_wp} reached")
                    else:
                        self.get_logger().error(f"Waypoint {self.current_wp} failed")
                    self.current_wp += 1
                    self.navigation_in_progress = False
        elif self.state == 'APPROACH':
            # 接近逻辑以后再实现，暂时留空
            pass
    
    def approach_blue(self, blue_center_x, blue_area, image_center=320):
        '''
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
        '''
        return self.get_logger().info(f"Functuion not finished")
    def stop(self):
        """stop robot"""
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)
        
    #def is_navigating(self):
        #return self.goal_client.is_navigating

    def record_blue_pose(self, robot_pose):
        
        self.blue_records.append(robot_pose)
        self.get_logger().info(f"Blue cube at {robot_pose}")
        

    '''
    def explore(self):
        # use Nav2 go to the next way point
        if self.current_wp >= len(self.waypoints):
            self.get_logger().info("explore done, no blue box")
            return False
        
        goal_x, goal_y = self.waypoints[self.current_wp]
        self.get_logger().info(f"Navigate to {self.current_wp}: ({goal_x}, {goal_y})")
        
        # send goal
        #self.goal_client.send_goal(goal_x, goal_y, 0.0)
        success, status = self.goal_client.send_goal_and_wait(goal_x, goal_y, timeout_sec=40.0)       
        
        if success:
            self.get_logger().info(f"Success to {self.current_wp}")
        else:
            self.get_logger().error(f"Failed to reach waypoint {self.current_wp} (status={status})")
        self.current_wp += 1
        return success
    '''