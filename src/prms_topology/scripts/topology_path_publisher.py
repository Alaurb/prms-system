#!/usr/bin/env python3
import math

import rospy
from geometry_msgs.msg import PoseStamped, Quaternion
from nav_msgs.msg import Path


def yaw_to_quaternion(yaw):
    half = yaw * 0.5
    return Quaternion(0.0, 0.0, math.sin(half), math.cos(half))


def waypoint_to_pose(waypoint, frame_id):
    pose = PoseStamped()
    pose.header.stamp = rospy.Time.now()
    pose.header.frame_id = frame_id
    pose.pose.position.x = float(waypoint.get("x", 0.0))
    pose.pose.position.y = float(waypoint.get("y", 0.0))
    pose.pose.position.z = float(waypoint.get("z", 0.0))
    pose.pose.orientation = yaw_to_quaternion(float(waypoint.get("yaw", 0.0)))
    return pose


class TopologyPathPublisher:
    def __init__(self):
        self.path_topic = rospy.get_param("/topics/topology_path", "/prms/topology/global_path")
        self.goal_topic = rospy.get_param("/topics/waypoint_goal", "/move_base_simple/goal")
        self.map_frame = rospy.get_param("/topology/map_frame", rospy.get_param("/frames/global", "map"))
        route_name = rospy.get_param("/topology/default_route", "demo_row_route")
        routes = rospy.get_param("/topology/routes", {})
        if route_name not in routes:
            raise rospy.ROSException("topology route not found: {}".format(route_name))
        self.route = routes[route_name]
        self.waypoints = self.route.get("waypoints", [])
        if not self.waypoints:
            raise rospy.ROSException("topology route has no waypoints")
        self.publish_goals = bool(self.route.get("publish_waypoint_goals", False))
        self.path_pub = rospy.Publisher(self.path_topic, Path, queue_size=1, latch=True)
        self.goal_pub = rospy.Publisher(self.goal_topic, PoseStamped, queue_size=1, latch=False)

    def make_path(self):
        path = Path()
        path.header.stamp = rospy.Time.now()
        path.header.frame_id = self.map_frame
        path.poses = [waypoint_to_pose(waypoint, self.map_frame) for waypoint in self.waypoints]
        for pose in path.poses:
            pose.header.stamp = path.header.stamp
        return path

    def spin(self):
        rate_hz = float(rospy.get_param("~rate", 1.0))
        rate = rospy.Rate(rate_hz)
        goal_index = 0
        while not rospy.is_shutdown():
            path = self.make_path()
            self.path_pub.publish(path)
            if self.publish_goals and goal_index < len(path.poses):
                self.goal_pub.publish(path.poses[goal_index])
                goal_index += 1
            rate.sleep()


def main():
    rospy.init_node("topology_path_publisher")
    TopologyPathPublisher().spin()


if __name__ == "__main__":
    main()

