import rclpy
from rclpy.node import Node

from aerocue_msgs.msg import MissionWaypoint


class MissionPlanner(Node):

    def __init__(self):
        super().__init__('mission_planner')

        # ==========================================
        # PARAMETERS
        # ==========================================

        self.declare_parameter('start_latitude', 13.0827)
        self.declare_parameter('start_longitude', 80.2707)

        self.declare_parameter('end_latitude', 13.0927)
        self.declare_parameter('end_longitude', 80.2807)

        self.declare_parameter('altitude', 50.0)

        self.declare_parameter('num_drones', 3)

        self.declare_parameter('waypoints_per_strip', 5)

        # Time between individual waypoint messages
        self.declare_parameter('publish_interval', 0.2)

        # ==========================================
        # READ PARAMETERS
        # ==========================================

        self.start_lat = self.get_parameter(
            'start_latitude'
        ).value

        self.start_lon = self.get_parameter(
            'start_longitude'
        ).value

        self.end_lat = self.get_parameter(
            'end_latitude'
        ).value

        self.end_lon = self.get_parameter(
            'end_longitude'
        ).value

        self.altitude = self.get_parameter(
            'altitude'
        ).value

        self.num_drones = self.get_parameter(
            'num_drones'
        ).value

        self.waypoints_per_strip = self.get_parameter(
            'waypoints_per_strip'
        ).value

        self.publish_interval = self.get_parameter(
            'publish_interval'
        ).value

        # ==========================================
        # PUBLISHER
        # ==========================================

        self.waypoint_publisher = self.create_publisher(
            MissionWaypoint,
            '/mission/waypoints',
            10
        )

        # ==========================================
        # WAYPOINT STORAGE
        # ==========================================

        self.waypoints = []

        self.publish_index = 0

        # ==========================================
        # STARTUP INFORMATION
        # ==========================================

        self.get_logger().info(
            'Mission Planner started!'
        )

        self.get_logger().info(
            f'Start: ({self.start_lat}, {self.start_lon})'
        )

        self.get_logger().info(
            f'End: ({self.end_lat}, {self.end_lon})'
        )

        self.get_logger().info(
            f'Altitude: {self.altitude} m'
        )

        self.get_logger().info(
            f'Number of drones: {self.num_drones}'
        )

        self.get_logger().info(
            f'Waypoints per strip: '
            f'{self.waypoints_per_strip}'
        )

        self.get_logger().info(
            f'Publish interval: '
            f'{self.publish_interval} s'
        )

        # ==========================================
        # CALCULATE STRIPS
        # ==========================================

        longitude_width = (
            self.end_lon - self.start_lon
        )

        strip_width = (
            longitude_width / self.num_drones
        )

        self.get_logger().info(
            f'Total longitude width: '
            f'{longitude_width:.6f} degrees'
        )

        self.get_logger().info(
            f'Strip width: '
            f'{strip_width:.6f} degrees'
        )

        # ==========================================
        # GENERATE WAYPOINTS
        # ==========================================

        for drone_id in range(
            1,
            self.num_drones + 1
        ):

            strip_start_lon = (
                self.start_lon
                + (drone_id - 1) * strip_width
            )

            strip_end_lon = (
                self.start_lon
                + drone_id * strip_width
            )

            self.get_logger().info(
                f'Drone {drone_id}: Longitude '
                f'{strip_start_lon:.6f} '
                f'to '
                f'{strip_end_lon:.6f}'
            )

            strip_center_lon = (
                strip_start_lon
                + strip_end_lon
            ) / 2.0

            for waypoint_number in range(
                1,
                self.waypoints_per_strip + 1
            ):

                if self.waypoints_per_strip == 1:

                    progress = 0.0

                else:

                    progress = (
                        (waypoint_number - 1)
                        / (self.waypoints_per_strip - 1)
                    )

                latitude = (
                    self.start_lat
                    + progress
                    * (self.end_lat - self.start_lat)
                )

                longitude = strip_center_lon

                waypoint = MissionWaypoint()

                waypoint.drone_id = drone_id
                waypoint.waypoint_number = waypoint_number
                waypoint.latitude = latitude
                waypoint.longitude = longitude
                waypoint.altitude = self.altitude

                self.waypoints.append(waypoint)

                self.get_logger().info(
                    f'Drone {drone_id} | '
                    f'WP {waypoint_number} | '
                    f'Lat: {latitude:.6f} | '
                    f'Lon: {longitude:.6f} | '
                    f'Alt: {self.altitude:.1f}'
                )

        self.get_logger().info(
            f'Generated {len(self.waypoints)} '
            f'total waypoints.'
        )

        self.get_logger().info(
            'Mission ready.'
        )

        # ==========================================
        # START PACED PUBLICATION
        # ==========================================

        self.timer = self.create_timer(
            self.publish_interval,
            self.publish_next_waypoint
        )

    # ==============================================
    # PUBLISH ONE WAYPOINT
    # ==============================================

    def publish_next_waypoint(self):

        if self.publish_index >= len(self.waypoints):

            self.get_logger().info(
                'All mission waypoints published.'
            )

            self.timer.cancel()

            return

        waypoint = self.waypoints[
            self.publish_index
        ]

        self.waypoint_publisher.publish(
            waypoint
        )

        self.get_logger().info(
            f'Published waypoint '
            f'{self.publish_index + 1}/'
            f'{len(self.waypoints)} | '
            f'Drone {waypoint.drone_id} | '
            f'WP {waypoint.waypoint_number}'
        )

        self.publish_index += 1


def main(args=None):

    rclpy.init(args=args)

    node = MissionPlanner()

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
