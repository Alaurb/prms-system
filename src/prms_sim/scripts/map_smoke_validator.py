#!/usr/bin/env python3
import math
import sys

import rospy
from nav_msgs.msg import OccupancyGrid, Odometry, Path


class MapSmokeValidator:
    def __init__(self):
        self.path_topic = rospy.get_param("/topics/topology_path", "/prms/topology/global_path")
        self.odom_topic = rospy.get_param("~odom_topic", "Odometry")
        self.timeout_s = float(rospy.get_param("~timeout_s", 15.0))
        self.min_distance_m = float(rospy.get_param("~min_distance_m", 0.5))
        self.map_msg = None
        self.path_msg = None
        self.first_xy = None
        self.last_xy = None
        rospy.Subscriber("/map", OccupancyGrid, self.on_map, queue_size=1)
        rospy.Subscriber(self.path_topic, Path, self.on_path, queue_size=1)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=20)

    def on_map(self, message):
        self.map_msg = message

    def on_path(self, message):
        self.path_msg = message

    def on_odom(self, message):
        xy = (message.pose.pose.position.x, message.pose.pose.position.y)
        if self.first_xy is None:
            self.first_xy = xy
        self.last_xy = xy

    def travelled(self):
        if self.first_xy is None or self.last_xy is None:
            return 0.0
        return math.hypot(self.last_xy[0] - self.first_xy[0], self.last_xy[1] - self.first_xy[1])

    def spin(self):
        start = rospy.Time.now()
        rate = rospy.Rate(10.0)
        while not rospy.is_shutdown():
            map_ok = self.map_msg is not None and self.map_msg.info.width > 0 and self.map_msg.info.height > 0
            path_count = len(self.path_msg.poses) if self.path_msg is not None else 0
            movement = self.travelled()
            if map_ok and path_count >= 2 and movement >= self.min_distance_m:
                rospy.loginfo(
                    "PRMS map smoke passed: map=%dx%d resolution=%.3f path_poses=%d travelled_m=%.3f",
                    self.map_msg.info.width,
                    self.map_msg.info.height,
                    self.map_msg.info.resolution,
                    path_count,
                    movement,
                )
                return 0
            if (rospy.Time.now() - start).to_sec() > self.timeout_s:
                rospy.logerr(
                    "PRMS map smoke failed: map_ok=%s path_poses=%d travelled_m=%.3f",
                    map_ok,
                    path_count,
                    movement,
                )
                return 1
            rate.sleep()
        return 1


def main():
    rospy.init_node("map_smoke_validator")
    sys.exit(MapSmokeValidator().spin())


if __name__ == "__main__":
    main()

