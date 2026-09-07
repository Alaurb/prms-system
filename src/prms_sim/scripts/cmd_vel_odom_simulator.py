#!/usr/bin/env python3
import math

import rospy
import tf2_ros
from geometry_msgs.msg import Quaternion, TransformStamped, Twist
from nav_msgs.msg import Odometry


def yaw_to_quaternion(yaw):
    half = yaw * 0.5
    return Quaternion(0.0, 0.0, math.sin(half), math.cos(half))


class CmdVelOdomSimulator:
    def __init__(self):
        self.map_frame = rospy.get_param("/topology/map_frame", rospy.get_param("/frames/global", "map"))
        self.base_frame = rospy.get_param("/frames/robot_base", "body")
        self.odom_topic = rospy.get_param("~odom_topic", "Odometry")
        self.cmd_vel_topic = rospy.get_param("~cmd_vel_topic", "cmd_vel")
        self.max_linear = float(rospy.get_param("~max_linear_mps", 0.6))
        self.max_angular = float(rospy.get_param("~max_angular_rps", 1.5))
        self.x = float(rospy.get_param("~initial_x", 0.0))
        self.y = float(rospy.get_param("~initial_y", 0.0))
        self.yaw = float(rospy.get_param("~initial_yaw", 0.0))
        self.cmd = Twist()
        self.previous_time = rospy.Time.now()
        self.odom_pub = rospy.Publisher(self.odom_topic, Odometry, queue_size=10)
        self.tf_pub = tf2_ros.TransformBroadcaster()
        rospy.Subscriber(self.cmd_vel_topic, Twist, self.on_cmd_vel, queue_size=10)

    def on_cmd_vel(self, message):
        self.cmd = message

    def step(self, dt):
        linear = max(-self.max_linear, min(self.max_linear, self.cmd.linear.x))
        angular = max(-self.max_angular, min(self.max_angular, self.cmd.angular.z))
        self.yaw += angular * dt
        self.x += linear * math.cos(self.yaw) * dt
        self.y += linear * math.sin(self.yaw) * dt

    def publish(self):
        stamp = rospy.Time.now()
        quat = yaw_to_quaternion(self.yaw)
        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = self.map_frame
        transform.child_frame_id = self.base_frame
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = 0.0
        transform.transform.rotation = quat
        self.tf_pub.sendTransform(transform)

        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self.map_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation = quat
        odom.twist.twist.linear.x = self.cmd.linear.x
        odom.twist.twist.angular.z = self.cmd.angular.z
        self.odom_pub.publish(odom)

    def spin(self):
        rate = rospy.Rate(float(rospy.get_param("~rate", 20.0)))
        while not rospy.is_shutdown():
            now = rospy.Time.now()
            dt = max(0.0, (now - self.previous_time).to_sec())
            self.previous_time = now
            self.step(dt)
            self.publish()
            rate.sleep()


def main():
    rospy.init_node("cmd_vel_odom_simulator")
    CmdVelOdomSimulator().spin()


if __name__ == "__main__":
    main()

