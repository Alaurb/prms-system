#!/usr/bin/env python3
import math

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry, Path


def clamp(value, low, high):
    return max(low, min(high, value))


def yaw_from_quaternion(q):
    siny = 2.0 * (q.w * q.z + q.x * q.y)
    cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny, cosy)


def wrap_angle(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


class SimplePathFollower:
    def __init__(self):
        self.path_topic = rospy.get_param("/topics/topology_path", "/prms/topology/global_path")
        self.odom_topic = rospy.get_param("~odom_topic", "Odometry")
        self.cmd_vel_topic = rospy.get_param("~cmd_vel_topic", "cmd_vel")
        self.lookahead_m = float(rospy.get_param("~lookahead_m", 0.45))
        self.goal_tolerance_m = float(rospy.get_param("~goal_tolerance_m", 0.15))
        self.max_linear = float(rospy.get_param("~max_linear_mps", 0.45))
        self.max_angular = float(rospy.get_param("~max_angular_rps", 1.2))
        self.linear_gain = float(rospy.get_param("~linear_gain", 0.8))
        self.angular_gain = float(rospy.get_param("~angular_gain", 2.0))
        self.path = []
        self.target_index = 0
        self.pose = None
        self.goal_reached = False
        self.cmd_pub = rospy.Publisher(self.cmd_vel_topic, Twist, queue_size=10)
        rospy.Subscriber(self.path_topic, Path, self.on_path, queue_size=1)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=10)

    def on_path(self, message):
        self.path = [(pose.pose.position.x, pose.pose.position.y) for pose in message.poses]
        self.target_index = min(self.target_index, max(len(self.path) - 1, 0))

    def on_odom(self, message):
        pose = message.pose.pose
        self.pose = (pose.position.x, pose.position.y, yaw_from_quaternion(pose.orientation))

    def choose_target(self):
        if not self.path or self.pose is None:
            return None
        x, y, _ = self.pose
        while self.target_index + 1 < len(self.path):
            target = self.path[self.target_index]
            if math.hypot(target[0] - x, target[1] - y) > self.lookahead_m:
                break
            self.target_index += 1
        return self.path[self.target_index]

    def make_command(self):
        cmd = Twist()
        if not self.path or self.pose is None or self.goal_reached:
            return cmd
        x, y, yaw = self.pose
        final = self.path[-1]
        final_dist = math.hypot(final[0] - x, final[1] - y)
        if final_dist <= self.goal_tolerance_m:
            self.goal_reached = True
            return cmd
        target = self.choose_target()
        if target is None:
            return cmd
        dx = target[0] - x
        dy = target[1] - y
        heading_error = wrap_angle(math.atan2(dy, dx) - yaw)
        cmd.linear.x = clamp(self.linear_gain * final_dist, 0.05, self.max_linear)
        if abs(heading_error) > 0.8:
            cmd.linear.x *= 0.35
        cmd.angular.z = clamp(self.angular_gain * heading_error, -self.max_angular, self.max_angular)
        return cmd

    def spin(self):
        rate = rospy.Rate(float(rospy.get_param("~rate", 10.0)))
        while not rospy.is_shutdown():
            self.cmd_pub.publish(self.make_command())
            rate.sleep()


def main():
    rospy.init_node("simple_path_follower")
    SimplePathFollower().spin()


if __name__ == "__main__":
    main()
