#!/usr/bin/env python3
import math
import sys

import rospy
from nav_msgs.msg import Odometry, Path


class RouteSmokeValidator:
    def __init__(self):
        self.path_topic = rospy.get_param("/topics/topology_path", "/prms/topology/global_path")
        self.odom_topic = rospy.get_param("~odom_topic", "Odometry")
        self.timeout_s = float(rospy.get_param("~timeout_s", 15.0))
        self.min_path_poses = int(rospy.get_param("~min_path_poses", 2))
        self.min_distance_m = float(rospy.get_param("~min_distance_m", 0.5))
        self.path = None
        self.first_xy = None
        self.last_xy = None
        self.odom_samples = 0
        rospy.Subscriber(self.path_topic, Path, self.on_path, queue_size=1)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=20)

    def on_path(self, message):
        self.path = message

    def on_odom(self, message):
        xy = (message.pose.pose.position.x, message.pose.pose.position.y)
        if self.first_xy is None:
            self.first_xy = xy
        self.last_xy = xy
        self.odom_samples += 1

    def travelled(self):
        if self.first_xy is None or self.last_xy is None:
            return 0.0
        return math.hypot(self.last_xy[0] - self.first_xy[0], self.last_xy[1] - self.first_xy[1])

    def spin(self):
        start = rospy.Time.now()
        rate = rospy.Rate(10.0)
        while not rospy.is_shutdown():
            path_count = len(self.path.poses) if self.path is not None else 0
            movement = self.travelled()
            if path_count >= self.min_path_poses and self.odom_samples >= 3 and movement >= self.min_distance_m:
                rospy.loginfo(
                    "PRMS simulation smoke passed: path_poses=%d odom_samples=%d travelled_m=%.3f",
                    path_count,
                    self.odom_samples,
                    movement,
                )
                return 0
            if (rospy.Time.now() - start).to_sec() > self.timeout_s:
                rospy.logerr(
                    "PRMS simulation smoke failed: path_poses=%d odom_samples=%d travelled_m=%.3f",
                    path_count,
                    self.odom_samples,
                    movement,
                )
                return 1
            rate.sleep()
        return 1


def main():
    rospy.init_node("route_smoke_validator")
    sys.exit(RouteSmokeValidator().spin())


if __name__ == "__main__":
    main()

