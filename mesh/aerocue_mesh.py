import socket
import json
import threading
import time
import uuid


# ============================================================
# AEROCUE MESH CONFIGURATION
# ============================================================

NETWORK_IP = "192.168.136.128"

DRONE_PORTS = {
    1: 5001,
    2: 5002,
    3: 5003
}

GCS_IP = "192.168.136.128"
GCS_PORT = 7000

GPS_INTERVAL = 2
HEARTBEAT_INTERVAL = 2


# ============================================================
# SIMULATED GPS POSITIONS
# ============================================================

DRONE_POSITIONS = {

    1: {
        "latitude": 13.082680,
        "longitude": 80.270718,
        "altitude": 120.5
    },

    2: {
        "latitude": 13.083500,
        "longitude": 80.270718,
        "altitude": 125.0
    },

    3: {
        "latitude": 13.084300,
        "longitude": 80.270718,
        "altitude": 118.0
    }
}


# ============================================================
# SELECT MODE
# ============================================================

def select_mode():

    print()
    print("========================================")
    print("          AEROCUE MESH SYSTEM")
    print("========================================")
    print()
    print("1. Software Simulation")
    print("2. Hardware")
    print()

    while True:

        choice = input("Select mode [1/2]: ")

        if choice == "1":
            return "SOFTWARE"

        if choice == "2":
            return "HARDWARE"

        print("Please enter 1 or 2.")


# ============================================================
# SELECT DRONE
# ============================================================

def select_drone():

    print()
    print("Select Drone")
    print("1. Drone 1")
    print("2. Drone 2")
    print("3. Drone 3")
    print()

    while True:

        choice = input("Enter Drone ID: ")

        if choice in ["1", "2", "3"]:
            return int(choice)

        print("Please enter 1, 2 or 3.")


# ============================================================
# GPS SOURCE
# ============================================================

class GPS:

    def __init__(self, drone_id, mode):

        self.drone_id = drone_id
        self.mode = mode

        self.latitude = DRONE_POSITIONS[drone_id]["latitude"]
        self.longitude = DRONE_POSITIONS[drone_id]["longitude"]
        self.altitude = DRONE_POSITIONS[drone_id]["altitude"]


    def get_position(self):

        if self.mode == "HARDWARE":

            return self.hardware_gps()

        return self.software_gps()


    # --------------------------------------------------------
    # SOFTWARE GPS
    # --------------------------------------------------------

    def software_gps(self):

        self.longitude += 0.000020

        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude
        }


    # --------------------------------------------------------
    # HARDWARE GPS
    #
    # Replace this function later with your GPS module code.
    # --------------------------------------------------------

    def hardware_gps(self):

        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude
        }


# ============================================================
# MESH DRONE
# ============================================================

class Drone:

    def __init__(self, drone_id, mode):

        self.drone_id = drone_id
        self.mode = mode

        self.port = DRONE_PORTS[drone_id]

        self.gps = GPS(
            drone_id,
            mode
        )

        self.running = True


    # ========================================================
    # RECEIVE GPS FROM OTHER DRONES
    # ========================================================

    def receiver(self):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        sock.bind(
            (
                NETWORK_IP,
                self.port
            )
        )

        print()
        print(
            f"🟩 Drone {self.drone_id} "
            f"receiver listening on "
            f"{NETWORK_IP}:{self.port}"
        )


        while self.running:

            try:

                data, address = sock.recvfrom(4096)

                packet = json.loads(
                    data.decode()
                )

                sender = packet.get(
                    "drone_id"
                )

                if sender == self.drone_id:
                    continue


                if packet.get("type") == "gps":

                    print()
                    print("📡 GPS RECEIVED")
                    print("----------------------------")

                    print(
                        f"From Drone : {sender}"
                    )

                    print(
                        f"Latitude   : "
                        f"{packet['latitude']:.6f}"
                    )

                    print(
                        f"Longitude  : "
                        f"{packet['longitude']:.6f}"
                    )

                    print(
                        f"Altitude   : "
                        f"{packet['altitude']:.1f} m"
                    )

                    print(
                        f"Timestamp  : "
                        f"{packet['timestamp']}"
                    )

                    print(
                        f"Source     : "
                        f"{address[0]}:{address[1]}"
                    )


            except Exception as e:

                print(
                    f"Receiver error: {e}"
                )


    # ========================================================
    # SEND GPS TO GCS
    # ========================================================

    def send_to_gcs(self, packet):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        try:

            data = json.dumps(
                packet
            ).encode()

            sock.sendto(
                data,
                (
                    GCS_IP,
                    GCS_PORT
                )
            )

            print(
                f"📡 Drone {self.drone_id} "
                f"→ GCS | "
                f"GPS sent to port {GCS_PORT}"
            )

        except Exception as e:

            print(
                f"GCS error: {e}"
            )

        finally:

            sock.close()


    # ========================================================
    # SEND GPS TO OTHER DRONES
    # ========================================================

    def sender(self):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        print()
        print(
            f"🟦 Drone {self.drone_id} "
            f"sender started"
        )


        while self.running:

            position = self.gps.get_position()


            packet = {

                "type": "gps",

                "packet_id":
                    str(uuid.uuid4()),

                "drone_id":
                    self.drone_id,

                "latitude":
                    position["latitude"],

                "longitude":
                    position["longitude"],

                "altitude":
                    position["altitude"],

                "timestamp":
                    time.time()
            }


            data = json.dumps(
                packet
            ).encode()


            # ------------------------------------------------
            # SEND TO GCS
            # ------------------------------------------------

            sock.sendto(
                data,
                (
                    GCS_IP,
                    GCS_PORT
                )
            )

            print(
                f"📡 Drone {self.drone_id} "
                f"→ GCS | "
                f"GPS: "
                f"{position['latitude']:.6f}, "
                f"{position['longitude']:.6f}, "
                f"{position['altitude']:.1f} m"
            )


            # ------------------------------------------------
            # SEND TO OTHER DRONES
            # ------------------------------------------------

            for target_drone, target_port in DRONE_PORTS.items():

                if target_drone == self.drone_id:
                    continue


                sock.sendto(
                    data,
                    (
                        NETWORK_IP,
                        target_port
                    )
                )


                print(
                    f"📤 Drone {self.drone_id} → "
                    f"Drone {target_drone} | "
                    f"GPS: "
                    f"{position['latitude']:.6f}, "
                    f"{position['longitude']:.6f}, "
                    f"{position['altitude']:.1f} m"
                )


            time.sleep(
                GPS_INTERVAL
            )


    # ========================================================
    # HEARTBEAT
    # ========================================================

    def heartbeat(self):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )


        while self.running:

            packet = {

                "type": "heartbeat",

                "drone_id":
                    self.drone_id,

                "timestamp":
                    time.time()
            }


            data = json.dumps(
                packet
            ).encode()


            for target_drone, target_port in DRONE_PORTS.items():

                if target_drone == self.drone_id:
                    continue


                sock.sendto(
                    data,
                    (
                        NETWORK_IP,
                        target_port
                    )
                )


            time.sleep(
                HEARTBEAT_INTERVAL
            )


    # ========================================================
    # START DRONE
    # ========================================================

    def start(self):

        print()
        print("========================================")
        print(
            f"🚁 AEROCUE DRONE {self.drone_id}"
        )
        print("========================================")

        print(
            f"Mode       : {self.mode}"
        )

        print(
            f"IP         : {NETWORK_IP}"
        )

        print(
            f"Drone Port : {self.port}"
        )

        print(
            f"GCS        : {GCS_IP}:{GCS_PORT}"
        )

        print(
            f"Other Drones: "
            f"{[d for d in DRONE_PORTS if d != self.drone_id]}"
        )

        print("========================================")


        threading.Thread(
            target=self.receiver,
            daemon=True
        ).start()


        threading.Thread(
            target=self.sender,
            daemon=True
        ).start()


        threading.Thread(
            target=self.heartbeat,
            daemon=True
        ).start()


        try:

            while True:

                time.sleep(1)

        except KeyboardInterrupt:

            self.running = False

            print(
                f"\n🛑 Drone {self.drone_id} stopped."
            )


# ============================================================
# MAIN
# ============================================================

def main():

    mode = select_mode()

    drone_id = select_drone()

    drone = Drone(
        drone_id,
        mode
    )

    drone.start()


if __name__ == "__main__":

    main()
