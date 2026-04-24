#!/usr/bin/env python3
import rclpy
import cv2
from rclpy.node import Node

from ros2_project_el23st.camera_subscriber import CameraSubscriber
from ros2_project_el23st.colour_mask import ColourMask
from ros2_project_el23st.object_detector import ObjectDetector
from ros2_project_el23st.robot_controller import RobotController

class ProjectMain(Node):
    def __init__(self):
        super().__init__('project_main')
        
        self.camera = CameraSubscriber()
        self.masker = ColourMask()
        self.detector = ObjectDetector()
        self.robot = RobotController()
        
        self.robot.navigator.waitUntilNav2Active()
        self.exploration_finished = False
        self.navigation_active = False
        
        self.get_logger().info("项目已启动，开始探索...")
    
    def run(self):
        while rclpy.ok():
            rclpy.spin_once(self.camera, timeout_sec=0.1)
            
            # 1. 更新导航状态（如果导航活跃）
            if self.navigation_active and self.robot.is_navigation_complete():
                self.navigation_active = False
                # 一个航点结束，如果探索未完成且没有检测到蓝色，稍后会自动启动下一个
                # 但这里需要检查是否所有航点都走完了
                if self.robot.current_wp >= len(self.robot.waypoints):
                    self.exploration_finished = True
                    self.get_logger().info("所有航点已访问，未发现蓝色方块")
            
            # 2. 获取图像并检测蓝色
            frame = self.camera.get_image()
            if frame is None:
                continue
            
            blue_mask = self.masker.get_blue_mask(frame)
            detected, area, center, bbox = self.detector.detect_blue(blue_mask, frame)
            
            # 显示图像（略）
            cv2.imshow('Camera Feed', frame)
            cv2.imshow('Blue Mask', blue_mask)
            red_mask = self.masker.get_red_mask(frame)
            green_mask = self.masker.get_green_mask(frame)
            cv2.imshow('Red Mask', red_mask)
            cv2.imshow('Green Mask', green_mask)
            
            key = cv2.waitKey(3) & 0xFF
            if key == ord('q'):
                break
            
            # 3. 决策逻辑
            if detected:
                # 看到蓝色 → 停止导航，切换到接近模式
                if self.navigation_active:
                    self.robot.cancel_navigation()
                    self.navigation_active = False
                
                if self.detector.is_close_enough(threshold=50000):
                    self.robot.stop()
                    self.get_logger().info("任务完成！已停在蓝色箱子附近")
                    break
                else:
                    self.robot.approach_blue(center[0], area)
            else:
                # 没看到蓝色 → 如果需要导航且未完成，则启动下一个航点
                if not self.exploration_finished and not self.navigation_active:
                    if self.robot.start_navigation():
                        self.navigation_active = True
        
        cv2.destroyAllWindows()

def main(args=None):
    rclpy.init(args=args)
    project = ProjectMain()
    project.run()
    project.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()