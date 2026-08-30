#!/home/sathwik/aerocue_ai_env/bin/python3

import rclpy
from rclpy.node import Node

from ultralytics import YOLO

from aerocue_msgs.msg import SurvivorDetection

import cv2
import os


class YoloNode(Node):

    def __init__(self):
        super().__init__('yolo_node')

        self.get_logger().info('Starting AeroCue AI YOLO Node...')

        # Publisher for survivor/object detections
        self.publisher_ = self.create_publisher(
            SurvivorDetection,
            '/survivor_detections',
            10
        )

        # Load YOLOv8 model
        model_path = os.path.expanduser('~/yolov8n.pt')

        self.get_logger().info(
            f'Loading YOLO model from: {model_path}'
        )

        self.model = YOLO(model_path)

        self.get_logger().info('YOLO model loaded successfully!')

        # Test image
        image_path = os.path.expanduser('~/bus.jpg')

        if not os.path.exists(image_path):
            self.get_logger().error(
                f'Test image not found: {image_path}'
            )
            return

        self.get_logger().info(
            f'Running YOLO detection on: {image_path}'
        )

        # Read image
        image = cv2.imread(image_path)

        if image is None:
            self.get_logger().error(
                'Could not read the test image.'
            )
            return

        # Run YOLO detection
        results = self.model(image)

        detected_count = 0

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                class_name = self.model.names[class_id]

                # Bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                width = x2 - x1
                height = y2 - y1

                detected_count += 1

                # Create ROS 2 detection message
                msg = SurvivorDetection()

                msg.drone_id = 1
                msg.class_name = class_name
                msg.confidence = confidence
                msg.x = float(x1)
                msg.y = float(y1)
                msg.width = float(width)
                msg.height = float(height)

                # Publish detection
                self.publisher_.publish(msg)

                self.get_logger().info(
                    f'Published: {class_name} '
                    f'(confidence: {confidence:.2f})'
                )

        self.get_logger().info(
            f'Total objects detected: {detected_count}'
        )

        self.get_logger().info(
            'AeroCue AI YOLO Node is running.'
        )


def main(args=None):

    rclpy.init(args=args)

    node = YoloNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
