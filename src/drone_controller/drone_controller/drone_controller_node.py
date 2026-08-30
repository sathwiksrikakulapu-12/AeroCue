import rclpy
from rclpy.node import Node

from aerocue_msgs.msg import MissionWaypoint
from aerocue_msgs.msg import SyncCommand


class DroneController(Node):

    def __init__(self):
        super().__init__('drone_controller')

        # ==========================================
        # PARAMETERS
        # ==========================================

        self.declare_parameter('num_drones', 3)
        self.declare_parameter('waypoints_per_strip', 5)

        self.num_drones = self.get_parameter(
            'num_drones'
        ).value

        self.waypoints_per_strip = self.get_parameter(
            'waypoints_per_strip'
        ).value

        # ==========================================
        # MISSION STORAGE
        # ==========================================

        self.mission = {}

        self.total_waypoints_received = 0

        self.current_waypoint = 1

        self.mission_started = False

        self.mission_complete = False

        # ==========================================
        # RECEIVE COMPLETE MISSION
        # ==========================================

        self.mission_subscription = self.create_subscription(
            MissionWaypoint,
            '/mission/waypoints',
            self.mission_callback,
            10
        )

        # ==========================================
        # RECEIVE SYNC COMMAND
        # ==========================================

        self.sync_subscription = self.create_subscription(
            SyncCommand,
            '/swarm/sync_command',
            self.sync_callback,
            10
        )

        # ==========================================
        # SEND CURRENT WAYPOINT TO SIMULATOR
        # ==========================================

        self.command_publisher = self.create_publisher(
            MissionWaypoint,
            '/drone/current_waypoint',
            10
        )

        self.get_logger().info(
            'Drone Controller started!'
        )

        self.get_logger().info(
            'Waiting for complete mission...'
        )

    # ==============================================
    # RECEIVE MISSION
    # ==============================================

    def mission_callback(self, msg):

        if self.mission_started:
            return

        drone_id = msg.drone_id
        waypoint_number = msg.waypoint_number

        if drone_id not in self.mission:
            self.mission[drone_id] = {}

        # Ignore duplicate waypoint messages
        if waypoint_number in self.mission[drone_id]:
            return

        self.mission[drone_id][waypoint_number] = msg

        self.total_waypoints_received += 1

        self.get_logger().info(
            f'Stored Drone {drone_id} '
            f'Waypoint {waypoint_number} '
            f'({self.total_waypoints_received}/'
            f'{self.expected_total_waypoints()})'
        )

        # ==========================================
        # START WHEN COMPLETE MISSION IS RECEIVED
        # ==========================================

        if (
            self.total_waypoints_received
            >= self.expected_total_waypoints()
            and self.all_mission_waypoints_received()
        ):

            self.mission_started = True

            self.get_logger().info(
                '=========================================='
            )

            self.get_logger().info(
                'ALL MISSION WAYPOINTS RECEIVED!'
            )

            self.get_logger().info(
                'STARTING SYNCHRONIZED MISSION'
            )

            self.get_logger().info(
                '=========================================='
            )

            self.release_current_waypoint()

    # ==============================================
    # EXPECTED NUMBER OF WAYPOINTS
    # ==============================================

    def expected_total_waypoints(self):

        return (
            self.num_drones
            * self.waypoints_per_strip
        )

    # ==============================================
    # VERIFY COMPLETE MISSION
    # ==============================================

    def all_mission_waypoints_received(self):

        for drone_id in range(
            1,
            self.num_drones + 1
        ):

            if drone_id not in self.mission:
                return False

            for waypoint_number in range(
                1,
                self.waypoints_per_strip + 1
            ):

                if (
                    waypoint_number
                    not in self.mission[drone_id]
                ):
                    return False

        return True

    # ==============================================
    # RELEASE CURRENT WAYPOINT
    # ==============================================

    def release_current_waypoint(self):

        if self.mission_complete:
            return

        self.get_logger().info(
            f'Releasing Waypoint '
            f'{self.current_waypoint} '
            f'to all drones...'
        )

        for drone_id in range(
            1,
            self.num_drones + 1
        ):

            waypoint = self.mission[
                drone_id
            ][
                self.current_waypoint
            ]

            self.command_publisher.publish(
                waypoint
            )

            self.get_logger().info(
                f'Commanded Drone {drone_id} '
                f'-> WP {self.current_waypoint}'
            )

    # ==============================================
    # RECEIVE SYNCHRONIZATION
    # ==============================================

    def sync_callback(self, msg):

        if not self.mission_started:
            return

        if self.mission_complete:
            return

        if (
            not msg.synchronized
            or
            msg.waypoint_number
            != self.current_waypoint
        ):
            return

        self.get_logger().info(
            f'=========================================='
        )

        self.get_logger().info(
            f'SWARM SYNCHRONIZED AT '
            f'WAYPOINT {self.current_waypoint}'
        )

        self.get_logger().info(
            f'=========================================='
        )

        # ==========================================
        # FINAL WAYPOINT
        # ==========================================

        if (
            self.current_waypoint
            >= self.waypoints_per_strip
        ):

            self.mission_complete = True

            self.get_logger().info(
                '******************************************'
            )

            self.get_logger().info(
                'MISSION COMPLETE!'
            )

            self.get_logger().info(
                'All drones completed the mission.'
            )

            self.get_logger().info(
                '******************************************'
            )

            return

        # ==========================================
        # MOVE TO NEXT WAYPOINT
        # ==========================================

        self.current_waypoint += 1

        self.get_logger().info(
            f'Advancing to Waypoint '
            f'{self.current_waypoint}'
        )

        self.release_current_waypoint()


def main(args=None):

    rclpy.init(args=args)

    node = DroneController()

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
