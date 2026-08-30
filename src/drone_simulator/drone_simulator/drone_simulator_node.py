import math

import rclpy
from rclpy.node import Node

from aerocue_msgs.msg import MissionWaypoint
from aerocue_msgs.msg import DroneStatus


class DroneSimulator(Node):

    def __init__(self):
        super().__init__('drone_simulator')

        # ==========================================
        # ACTIVE DRONE TARGETS
        # ==========================================

        self.targets = {}

        # Current position of each drone
        self.positions = {}

        # Whether each drone reached its target
        self.reached = {}

        # ==========================================
        # RECEIVE CURRENT WAYPOINT
        # ==========================================

        self.command_subscription = self.create_subscription(
            MissionWaypoint,
            '/drone/current_waypoint',
            self.command_callback,
            10
        )

        # ==========================================
        # PUBLISH DRONE STATUS
        # ==========================================

        self.status_publisher = self.create_publisher(
            DroneStatus,
            '/drone/status',
            10
        )

        # ==========================================
        # MOVEMENT TIMER
        # ==========================================

        self.timer = self.create_timer(
            0.5,
            self.update_drones
        )

        # Movement speed
        self.speed = 0.0005

        # Arrival threshold
        self.threshold = 0.00005

        self.get_logger().info(
            'Drone Simulator started!'
        )

        self.get_logger().info(
            'Waiting for commands from Drone Controller...'
        )

    # ==============================================
    # RECEIVE WAYPOINT COMMAND
    # ==============================================

    def command_callback(self, msg):

        drone_id = msg.drone_id

        # Save the active target
        self.targets[drone_id] = msg

        # New command means drone has not reached
        # the new target yet.
        self.reached[drone_id] = False

        # ==========================================
        # INITIALIZE DRONE POSITION
        # ==========================================

        if drone_id not in self.positions:

            self.positions[drone_id] = {
                'latitude': msg.latitude - 0.001,
                'longitude': msg.longitude - 0.001,
                'altitude': msg.altitude
            }

            self.get_logger().info(
                f'Drone {drone_id} initialized '
                f'for WP {msg.waypoint_number}'
            )

        else:

            self.get_logger().info(
                f'Drone {drone_id} moving to '
                f'WP {msg.waypoint_number}'
            )

    # ==============================================
    # UPDATE DRONES
    # ==============================================

    def update_drones(self):

        for drone_id in list(
            self.targets.keys()
        ):

            target = self.targets[drone_id]

            position = self.positions[drone_id]

            # ======================================
            # ALREADY REACHED
            # ======================================

            if self.reached.get(
                drone_id,
                False
            ):

                # Keep reporting the reached state
                # while waiting for the next command.
                self.publish_status(
                    drone_id,
                    target
                )

                continue

            # ======================================
            # CURRENT POSITION
            # ======================================

            current_lat = position[
                'latitude'
            ]

            current_lon = position[
                'longitude'
            ]

            current_alt = position[
                'altitude'
            ]

            # ======================================
            # DISTANCE TO TARGET
            # ======================================

            d_lat = (
                target.latitude
                - current_lat
            )

            d_lon = (
                target.longitude
                - current_lon
            )

            d_alt = (
                target.altitude
                - current_alt
            )

            distance = math.sqrt(
                d_lat ** 2
                + d_lon ** 2
                + (d_alt / 100000.0) ** 2
            )

            # ======================================
            # TARGET REACHED
            # ======================================

            if distance <= self.threshold:

                position[
                    'latitude'
                ] = target.latitude

                position[
                    'longitude'
                ] = target.longitude

                position[
                    'altitude'
                ] = target.altitude

                self.reached[drone_id] = True

                self.get_logger().info(
                    f'Drone {drone_id} '
                    f'REACHED WP '
                    f'{target.waypoint_number} '
                    f'- WAITING FOR SYNC'
                )

            # ======================================
            # MOVE TOWARD TARGET
            # ======================================

            else:

                position[
                    'latitude'
                ] += (
                    d_lat / distance
                ) * self.speed

                position[
                    'longitude'
                ] += (
                    d_lon / distance
                ) * self.speed

                position[
                    'altitude'
                ] += (
                    d_alt / distance
                ) * self.speed

            # ======================================
            # PUBLISH STATUS
            # ======================================

            self.publish_status(
                drone_id,
                target
            )

    # ==============================================
    # PUBLISH DRONE STATUS
    # ==============================================

    def publish_status(
        self,
        drone_id,
        target
    ):

        position = self.positions[
            drone_id
        ]

        msg = DroneStatus()

        msg.drone_id = drone_id

        msg.current_waypoint = (
            target.waypoint_number
        )

        msg.latitude = position[
            'latitude'
        ]

        msg.longitude = position[
            'longitude'
        ]

        msg.altitude = position[
            'altitude'
        ]

        msg.waypoint_reached = (
            self.reached.get(
                drone_id,
                False
            )
        )

        self.status_publisher.publish(
            msg
        )


def main(args=None):

    rclpy.init(args=args)

    node = DroneSimulator()

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
