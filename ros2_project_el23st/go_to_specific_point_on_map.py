import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from math import sin, cos

class GoToPose(Node):
    def __init__(self):
        super().__init__('go_to_pose_client')
        self.action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.current_goal_handle = None
        self.goal_done = False
        self.goal_success = False

    def send_goal_nonblocking(self, x, y, yaw=0.0):
        """非阻塞发送导航目标，立即返回"""
        self.goal_done = False
        self.goal_success = False
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.z = sin(yaw / 2)
        goal_msg.pose.pose.orientation.w = cos(yaw / 2)

        self.action_client.wait_for_server()
        send_future = self.action_client.send_goal_async(goal_msg)
        send_future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future):
        self.current_goal_handle = future.result()
        if not self.current_goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            self.goal_done = True
            self.goal_success = False
            return
        self.get_logger().info('Goal accepted')
        result_future = self.current_goal_handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _result_callback(self, future):
        result = future.result()
        self.goal_success = (result.status == 4)
        self.goal_done = True
        self.get_logger().info(f'Navigation done, success={self.goal_success}')

    def is_goal_finished(self):
        return self.goal_done

    def is_goal_successful(self):
        return self.goal_success