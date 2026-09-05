#!/usr/bin/env python3
import copy

import rospy
import tf2_ros
from prms_msgs.msg import MaturityObservationArray


class MaturityFusionNode:
    def __init__(self):
        self.input_topic = rospy.get_param("/topics/detections", "/prms/perception/detections")
        self.output_topic = rospy.get_param("/topics/fused_observations", "/prms/fusion/observations")
        self.global_frame = rospy.get_param("/frames/global", "map")
        self.camera_frame = rospy.get_param("/frames/panoramic_camera", "panoramic_camera")
        self.tf_buffer = tf2_ros.Buffer(rospy.Duration(10.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.publisher = rospy.Publisher(self.output_topic, MaturityObservationArray, queue_size=1, latch=True)
        self.subscriber = rospy.Subscriber(self.input_topic, MaturityObservationArray, self.on_detections, queue_size=1)

    def on_detections(self, message):
        fused = copy.deepcopy(message)
        fused.header.frame_id = self.global_frame
        try:
            transform = self.tf_buffer.lookup_transform(
                self.global_frame,
                self.camera_frame,
                message.header.stamp,
                rospy.Duration(0.05),
            )
            source = "tf_aligned"
        except Exception as exc:
            rospy.logwarn_throttle(5.0, "TF alignment unavailable: %s", exc)
            transform = None
            source = "unfused_no_tf"

        for detection in fused.detections:
            detection.header = fused.header
            if transform is not None and detection.position_source in ("", "unfused"):
                detection.map_x = transform.transform.translation.x
                detection.map_y = transform.transform.translation.y
                detection.map_z = transform.transform.translation.z
            if detection.position_source in ("", "unfused"):
                detection.position_source = source
        self.publisher.publish(fused)

    def spin(self):
        rospy.spin()


def main():
    rospy.init_node("maturity_fusion_node")
    MaturityFusionNode().spin()


if __name__ == "__main__":
    main()

