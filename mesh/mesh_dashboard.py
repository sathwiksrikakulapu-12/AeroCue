import socket
import json
import threading
import time
import os


# ============================================================
# AEROCUE GCS DASHBOARD
# ============================================================

NETWORK_IP = "192.168.136.128"

GCS_PORT = 7000

TIMEOUT = 6


# ============================================================
# DRONE DATA
# ============================================================

drones = {

    1: {
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 0.0,
        "last_seen": 0,
        "packets": 0
    },

    2: {
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 0.0,
        "last_seen": 0,
        "packets": 0
    },

    3: {
        "latitude": 0.0,
        "longitude": 0.0,
        "altitude": 0.0,
        "last_seen": 0,
        "packets": 0
    }
}


lock = threading.Lock()


# ============================================================
# RECEIVER
# ============================================================

def receiver():

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
            GCS_PORT
        )
    )


    print(
        f"GCS listening on "
        f"{NETWORK_IP}:{GCS_PORT}"
    )


    while True:

        try:

            data, address = sock.recvfrom(
                4096
            )

            packet = json.loads(
                data.decode()
            )


            if packet.get("type") != "gps":

                continue


            drone_id = packet.get(
                "drone_id"
            )


            if drone_id not in drones:

                continue


            with lock:

                drones[drone_id][
                    "latitude"
                ] = packet["latitude"]

                drones[drone_id][
                    "longitude"
                ] = packet["longitude"]

                drones[drone_id][
                    "altitude"
                ] = packet["altitude"]

                drones[drone_id][
                    "last_seen"
                ] = time.time()

                drones[drone_id][
                    "packets"
                ] += 1


        except Exception as error:

            print(
                f"GCS error: {error}"
            )


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    while True:

        os.system("clear")


        print()
        print("=" * 78)
        print("                    🚁 AEROCUE GCS")
        print("=" * 78)
        print()

        print(
            f"Network: {NETWORK_IP}"
        )

        print(
            f"GCS UDP Port: {GCS_PORT}"
        )

        print()


        print(
            f"{'DRONE':<10}"
            f"{'STATUS':<14}"
            f"{'LATITUDE':<15}"
            f"{'LONGITUDE':<15}"
            f"{'ALTITUDE':<12}"
            f"{'PACKETS':<10}"
        )

        print("-" * 78)


        now = time.time()

        online_count = 0

        total_packets = 0


        with lock:

            for drone_id in [1, 2, 3]:

                drone = drones[drone_id]


                last_seen = drone[
                    "last_seen"
                ]


                if last_seen == 0:

                    status = "🟡 WAITING"

                elif now - last_seen <= TIMEOUT:

                    status = "🟢 ONLINE"

                    online_count += 1

                else:

                    status = "🔴 OFFLINE"


                total_packets += drone[
                    "packets"
                ]


                print(
                    f"Drone {drone_id:<4}"
                    f"{status:<14}"
                    f"{drone['latitude']:<15.6f}"
                    f"{drone['longitude']:<15.6f}"
                    f"{drone['altitude']:<12.1f}"
                    f"{drone['packets']:<10}"
                )


        print()
        print("=" * 78)
        print("                    MESH NETWORK")
        print("=" * 78)
        print()

        print(
            "                  🚁 DRONE 1"
        )

        print(
            "                  ↕       ↕"
        )

        print(
            "             🚁 DRONE 2 ↔ 🚁 DRONE 3"
        )

        print()

        print(
            f"Active drones : "
            f"{online_count}/3"
        )

        print(
            f"GPS packets   : "
            f"{total_packets}"
        )

        print()

        print(
            "📡 GPS data is being received "
            "by the GCS"
        )

        print(
            "Press Ctrl+C to exit"
        )


        time.sleep(1)


# ============================================================
# MAIN
# ============================================================

def main():

    threading.Thread(
        target=receiver,
        daemon=True
    ).start()


    time.sleep(1)


    try:

        dashboard()

    except KeyboardInterrupt:

        print(
            "\n🛑 GCS Dashboard stopped."
        )


if __name__ == "__main__":

    main()
