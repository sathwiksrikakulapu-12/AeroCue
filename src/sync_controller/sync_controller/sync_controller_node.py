import rclpy
from rclpy.node import Node

from aerocue_msgs.msg import DroneStatus
from aerocue_msgs.msg import SyncCommand


class SyncController(Node):

    def __init__(self):
        super().__init__('sync_controller')

        # ==========================================
        # NUMBER OF DRONES
        # ==========================================

        self.declare_parameter('num_drones', 3)

        self.num_drones = self.get_parameter(
            'num_drones'
        ).value

        # ==========================================
        # STORE LAST REACHED WAYPOINT
        # ==========================================

        self.reached_waypoints = {}

        # ==========================================
        # SUBSCRIBE TO DRONE STATUS
        # ==========================================

        self.subscription = self.create_subscription(
            DroneStatus,
            '/drone/status',
            self.status_callback,
            10
        )

        # ==========================================
        # PUBLISH SYNC COMMAND
        # ==========================================

        self.sync_publisher = self.create_publisher(
            SyncCommand,
            '/swarm/sync_command',
            10
        )

        # Prevent repeatedly publishing the same
        # synchronization command.
        self.last_synced_waypoint = 0

        self.get_logger().info(
            'Sync Controller started!'
        )

        self.get_logger().info(
            f'Waiting for {self.num_drones} drone statuses...'
        )

    # ==============================================
    # DRONE STATUS CALLBACK
    # ==============================================

    def status_callback(self, msg):

        # Ignore movement/status messages that do
        # not indicate the waypoint was actually reached.
        if not msg.waypoint_reached:
            return

        drone_id = msg.drone_id
        waypoint = msg.current_waypoint

        self.reached_waypoints[drone_id] = waypoint

        self.get_logger().info(
            f'Drone {drone_id} reached '
            f'Waypoint {waypoint}'
        )

        self.check_synchronization()

    # ==============================================
    # CHECK SWARM SYNCHRONIZATION
    # ==============================================

    def check_synchronization(self):

        # Wait until all expected drones report.
        if len(self.reached_waypoints) < self.num_drones:
            return

        waypoint_numbers = list(
            self.reached_waypoints.values()
        )

        # ==========================================
        # ALL DRONES AT SAME WAYPOINT
        # ==========================================

        if len(set(waypoint_numbers)) == 1:

            current_waypoint = waypoint_numbers[0]

            # Don't repeatedly send the same command.
            if current_waypoint == self.last_synced_waypoint:
                return

            self.last_synced_waypoint = current_waypoint

            command = SyncCommand()

            command.waypoint_number = current_waypoint
            command.synchronized = True

            self.sync_publisher.publish(command)

            self.get_logger().info(
                f'ALL DRONES SYNCHRONIZED at '
                f'Waypoint {current_waypoint}'
            )

            self.get_logger().info(
                f'Releasing swarm to next waypoint'
            )

        # ==========================================
        # NOT SYNCHRONIZED
        # ==========================================

        else:

            self.get_logger().info(
                f'Drones not synchronized: '
                f'{self.reached_waypoints}'
            )


def main(args=None):

    rclpy.init(args=args)

    node = SyncController()

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
