#!/usr/bin/env python3
"""Minimal keyboard teleoperation example for the Dog Factory project."""

import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class KeyboardTeleop(Node):
    def __init__(self) -> None:
        super().__init__("keyboard_teleop")
        self.publisher = self.create_publisher(Twist, "cmd_vel", 10)
        self.linear_speed = 0.3
        self.angular_speed = 0.6

    def get_key(self) -> str:
        fd = sys.stdin.fileno()
        settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, settings)

    def run(self) -> None:
        message = Twist()
        while rclpy.ok():
            key = self.get_key()
            if key == "z":
                message.linear.x = self.linear_speed
                message.angular.z = 0.0
            elif key == "s":
                message.linear.x = -self.linear_speed
                message.angular.z = 0.0
            elif key == "q":
                message.linear.x = 0.0
                message.angular.z = self.angular_speed
            elif key == "d":
                message.linear.x = 0.0
                message.angular.z = -self.angular_speed
            elif key == " ":
                message = Twist()
            elif key == "\x03":
                break
            self.publisher.publish(message)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = KeyboardTeleop()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
