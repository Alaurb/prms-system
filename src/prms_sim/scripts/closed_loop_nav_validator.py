#!/usr/bin/env python3
import json
import math
from pathlib import Path as FilePath
import sys

import rospy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry, Path


class ClosedLoopNavValidator:
    def __init__(self):
        self.path_topic = rospy.get_param("/topics/topology_path", "/prms/topology/global_path")
        self.odom_topic = rospy.get_param("~odom_topic", "Odometry")
        self.cmd_vel_topic = rospy.get_param("~cmd_vel_topic", "cmd_vel")
        self.timeout_s = float(rospy.get_param("~timeout_s", 30.0))
        self.goal_tolerance_m = float(rospy.get_param("~goal_tolerance_m", 0.2))
        self.min_cmd_samples = int(rospy.get_param("~min_cmd_samples", 5))
        self.trace_output = rospy.get_param("~trace_output", "")
        self.path = None
        self.last_xy = None
        self.cmd_samples = 0
        self.max_speed_seen = 0.0
        self.odom_trace = []
        self.cmd_trace = []
        rospy.Subscriber(self.path_topic, Path, self.on_path, queue_size=1)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=20)
        rospy.Subscriber(self.cmd_vel_topic, Twist, self.on_cmd_vel, queue_size=20)

    def on_path(self, message):
        self.path = message

    def on_odom(self, message):
        stamp = message.header.stamp.to_sec() if message.header.stamp else rospy.Time.now().to_sec()
        pose = message.pose.pose
        self.last_xy = (pose.position.x, pose.position.y)
        self.odom_trace.append(
            {
                "t": round(stamp, 3),
                "x_m": round(pose.position.x, 4),
                "y_m": round(pose.position.y, 4),
            }
        )

    def on_cmd_vel(self, message):
        stamp = rospy.Time.now().to_sec()
        self.cmd_samples += 1
        self.max_speed_seen = max(self.max_speed_seen, abs(message.linear.x) + abs(message.angular.z))
        self.cmd_trace.append(
            {
                "t": round(stamp, 3),
                "linear_mps": round(message.linear.x, 4),
                "angular_rps": round(message.angular.z, 4),
            }
        )

    def distance_to_goal(self):
        if self.path is None or self.last_xy is None or not self.path.poses:
            return None
        goal = self.path.poses[-1].pose.position
        return math.hypot(goal.x - self.last_xy[0], goal.y - self.last_xy[1])

    def path_points(self):
        if self.path is None:
            return []
        return [
            {
                "x_m": round(pose.pose.position.x, 4),
                "y_m": round(pose.pose.position.y, 4),
            }
            for pose in self.path.poses
        ]

    def write_trace(self, status, final_error_m):
        if not self.trace_output:
            return
        output_path = FilePath(self.trace_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "prms.nav_smoke_trace.v1",
            "status": status,
            "route": "demo_row_route",
            "map": {
                "name": "greenhouse_reference",
                "resolution_m_per_px": 0.05,
                "width_m": 6.8,
                "height_m": 1.3,
                "rows_y_m": [-0.48, -0.18, 0.18, 0.48],
            },
            "goal_tolerance_m": self.goal_tolerance_m,
            "final_error_m": None if final_error_m is None else round(final_error_m, 4),
            "cmd_samples": self.cmd_samples,
            "max_speed_seen": round(self.max_speed_seen, 4),
            "path": self.path_points(),
            "odometry": self.odom_trace[-1200:],
            "cmd_vel": self.cmd_trace[-1200:],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        rospy.loginfo("PRMS navigation trace written to %s", output_path)

    def spin(self):
        start = rospy.Time.now()
        rate = rospy.Rate(10.0)
        while not rospy.is_shutdown():
            path_count = len(self.path.poses) if self.path is not None else 0
            goal_dist = self.distance_to_goal()
            if (
                path_count >= 2
                and goal_dist is not None
                and goal_dist <= self.goal_tolerance_m
                and self.cmd_samples >= self.min_cmd_samples
                and self.max_speed_seen > 0.01
            ):
                rospy.loginfo(
                    "PRMS closed-loop navigation smoke passed: path_poses=%d cmd_samples=%d final_error_m=%.3f",
                    path_count,
                    self.cmd_samples,
                    goal_dist,
                )
                self.write_trace("passed", goal_dist)
                return 0
            if (rospy.Time.now() - start).to_sec() > self.timeout_s:
                rospy.logerr(
                    "PRMS closed-loop navigation smoke failed: path_poses=%d cmd_samples=%d final_error_m=%s",
                    path_count,
                    self.cmd_samples,
                    "none" if goal_dist is None else "{:.3f}".format(goal_dist),
                )
                self.write_trace("failed", goal_dist)
                return 1
            rate.sleep()
        return 1


def main():
    rospy.init_node("closed_loop_nav_validator")
    sys.exit(ClosedLoopNavValidator().spin())


if __name__ == "__main__":
    main()
