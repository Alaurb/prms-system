#!/usr/bin/env python3
import math

import rospy
import tf2_ros
from geometry_msgs.msg import Quaternion, TransformStamped
from nav_msgs.msg import Odometry


def yaw_to_quaternion(yaw):
    half = yaw * 0.5
    return Quaternion(0.0, 0.0, math.sin(half), math.cos(half))


def distance(a, b):
    return math.hypot(float(b.get("x", 0.0)) - float(a.get("x", 0.0)), float(b.get("y", 0.0)) - float(a.get("y", 0.0)))


class SimulatedLocalizationNode:
    def __init__(self):
        self.map_frame = rospy.get_param("/topology/map_frame", rospy.get_param("/frames/global", "map"))
        self.base_frame = rospy.get_param("/frames/robot_base", "body")
        self.odom_topic = rospy.get_param("~odom_topic", "Odometry")
        self.speed = max(0.01, float(rospy.get_param("~speed_mps", 0.35)))
        self.loop = bool(rospy.get_param("~loop", False))
        route_name = rospy.get_param("/topology/default_route", "demo_row_route")
        routes = rospy.get_param("/topology/routes", {})
        if route_name not in routes:
            raise rospy.ROSException("topology route not found: {}".format(route_name))
        self.waypoints = routes[route_name].get("waypoints", [])
        if len(self.waypoints) < 2:
            raise rospy.ROSException("simulation route requires at least two waypoints")
        self.odom_pub = rospy.Publisher(self.odom_topic, Odometry, queue_size=10)
        self.tf_pub = tf2_ros.TransformBroadcaster()
        self.segment_index = 0
        self.segment_progress = 0.0
        self.current = self.waypoints[0]
        self.previous_time = rospy.Time.now()

    def interpolate_pose(self, dt):
        while True:
            start = self.waypoints[self.segment_index]
            end = self.waypoints[self.segment_index + 1]
            segment_length = max(distance(start, end), 1e-6)
            self.segment_progress += self.speed * dt / segment_length
            if self.segment_progress <= 1.0:
                break
            if self.segment_index + 2 >= len(self.waypoints):
                if not self.loop:
                    self.segment_progress = 1.0
                    break
                self.segment_index = 0
                self.segment_progress = 0.0
            else:
                self.segment_index += 1
                self.segment_progress -= 1.0

        start = self.waypoints[self.segment_index]
        end = self.waypoints[self.segment_index + 1]
        ratio = self.segment_progress
        x = float(start.get("x", 0.0)) + (float(end.get("x", 0.0)) - float(start.get("x", 0.0))) * ratio
        y = float(start.get("y", 0.0)) + (float(end.get("y", 0.0)) - float(start.get("y", 0.0))) * ratio
        yaw = math.atan2(float(end.get("y", 0.0)) - float(start.get("y", 0.0)), float(end.get("x", 0.0)) - float(start.get("x", 0.0)))
        return x, y, yaw

    def publish_pose(self, x, y, yaw):
        stamp = rospy.Time.now()
        quat = yaw_to_quaternion(yaw)

        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = self.map_frame
        transform.child_frame_id = self.base_frame
        transform.transform.translation.x = x
        transform.transform.translation.y = y
        transform.transform.translation.z = 0.0
        transform.transform.rotation = quat
        self.tf_pub.sendTransform(transform)

        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = self.map_frame
        odom.child_frame_id = self.base_frame
        odom.pose.pose.position.x = x
        odom.pose.pose.position.y = y
        odom.pose.pose.orientation = quat
        odom.twist.twist.linear.x = self.speed
        self.odom_pub.publish(odom)

    def spin(self):
        rate = rospy.Rate(float(rospy.get_param("~rate", 10.0)))
        while not rospy.is_shutdown():
            now = rospy.Time.now()
            dt = max(0.0, (now - self.previous_time).to_sec())
            self.previous_time = now
            x, y, yaw = self.interpolate_pose(dt)
            self.publish_pose(x, y, yaw)
            rate.sleep()


def main():
    rospy.init_node("simulated_localization_node")
    SimulatedLocalizationNode().spin()


if __name__ == "__main__":
    main()

