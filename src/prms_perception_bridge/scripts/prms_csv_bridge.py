#!/usr/bin/env python3
import csv
from pathlib import Path

import rospy
from prms_msgs.msg import MaturityDetection, MaturityObservationArray


def _float(row, key, default=0.0):
    value = row.get(key, "")
    if value in ("", None):
        return default
    return float(value)


def detection_from_row(row):
    msg = MaturityDetection()
    msg.frame_id = row.get("frame", row.get("frame_id", ""))
    msg.side = row.get("side", "")
    msg.class_name = row.get("class_name", row.get("maturity", ""))
    msg.confidence = _float(row, "confidence")
    msg.bbox_cx = _float(row, "cx", _float(row, "bbox_cx"))
    msg.bbox_cy = _float(row, "cy", _float(row, "bbox_cy"))
    msg.bbox_w = _float(row, "w", _float(row, "bbox_w"))
    msg.bbox_h = _float(row, "h", _float(row, "bbox_h"))
    msg.map_x = _float(row, "x", _float(row, "map_x"))
    msg.map_y = _float(row, "y", _float(row, "map_y"))
    msg.map_z = _float(row, "z", _float(row, "map_z"))
    msg.position_source = row.get("position_source", "unfused")
    msg.track_id = row.get("track_id", "")
    return msg


class PrmsCsvBridge:
    def __init__(self):
        self.csv_path = Path(rospy.get_param("/perception/prms/detections_csv", ""))
        self.topic = rospy.get_param("/topics/detections", "/prms/perception/detections")
        self.frame = rospy.get_param("/frames/panoramic_camera", "panoramic_camera")
        self.loop = bool(rospy.get_param("~loop", False))
        self.rate = rospy.Rate(float(rospy.get_param("~rate", 1.0)))
        self.publisher = rospy.Publisher(self.topic, MaturityObservationArray, queue_size=1, latch=True)

    def load_rows(self):
        if not self.csv_path.exists():
            rospy.logwarn("PRMS detections CSV not found: %s", self.csv_path)
            return []
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def publish_once(self):
        rows = self.load_rows()
        message = MaturityObservationArray()
        message.header.stamp = rospy.Time.now()
        message.header.frame_id = self.frame
        message.detections = [detection_from_row(row) for row in rows]
        for det in message.detections:
            det.header = message.header
        self.publisher.publish(message)
        rospy.loginfo("published %d PRMS detections", len(message.detections))

    def spin(self):
        while not rospy.is_shutdown():
            self.publish_once()
            if not self.loop:
                rospy.spin()
                return
            self.rate.sleep()


def main():
    rospy.init_node("prms_csv_bridge")
    PrmsCsvBridge().spin()


if __name__ == "__main__":
    main()

