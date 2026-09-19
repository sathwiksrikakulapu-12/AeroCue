import socket
import json
import threading
import time
import sys


# ============================================================
# NETWORK CONFIGURATION
# ============================================================

# IP address of this Ubuntu VM
NETWORK_IP = "192.168.136.128"

# Base port
BASE_PORT = 5000


# ============================================================
# DRONE CONFIGURATION
# ============================================================

DRONES = {

    1: {
        "latitude": 13.082680,
        "longitude": 80.270718,
        "altitude": 120.5,
        "direction": 1
    },

    2: {
        "latitude": 13.083500,
        "longitude": 80.270718,
        "altitude": 125.0,
        "direction": 1
    },

    3: {
        "latitude": 13.084300,
        "longitude": 80.270718,
        "altitude": 118.0,
        "direction": 1
    }
}


# ============================================================
# SEARCH AREA
# ============================================================

START_LONGITUDE = 80.270718
END_LONGITUDE = 80.275000

# How much the drone moves every update
LONGITUDE_STEP = 0.000020

# GPS update interval
UPDATE_INTERVAL = 2


# ============================================================
# GET DRONE ID
# ============================================================

if len(sys.argv) != 2:

    print()
    print("Usage:")
    print("  python3 drone.py 1")
    print("  python3 drone.py 2")
    print("  python3 drone.py 3")
    print()

    sys.exit(1)


try:

    DRONE_ID = int(sys.argv[1])

except ValueError:

    print("Drone ID must be 1, 2 or 3.")

    sys.exit(1)


if DRONE_ID not in DRONES:

    print("Invalid drone ID.")

    print("Use:")
    print("1")
    print("2")
    print("3")

    sys.exit(1)


# ============================================================
# INITIAL GPS
# ============================================================

my_gps = DRONES[DRONE_ID].copy()

# Each drone gets its own UDP port
MY_PORT = BASE_PORT + DRONE_ID


# ============================================================
# OTHER DRONES
# ============================================================

OTHER_DRONES = {}

for drone_id in DRONES:

    if drone_id != DRONE_ID:

        OTHER_DRONES[drone_id] = BASE_PORT + drone_id


# ============================================================
# MOVE DRONE
# ============================================================

def update_position():

    step = LONGITUDE_STEP * my_gps["direction"]

    my_gps["longitude"] += step


    # Reached end of search area
    if my_gps["longitude"] >= END_LONGITUDE:

        my_gps["longitude"] = END_LONGITUDE

        my_gps["direction"] = -1

        print()
        print(
            f"🔄 Drone {DRONE_ID} reached "
            f"the end of its search strip."
        )

        print(
            f"↩️ Drone {DRONE_ID} reversing direction."
        )


    # Reached beginning of search area
    elif my_gps["longitude"] <= START_LONGITUDE:

        my_gps["longitude"] = START_LONGITUDE

        my_gps["direction"] = 1

        print()
        print(
            f"🔄 Drone {DRONE_ID} reached "
            f"the beginning of its search strip."
        )

        print(
            f"↪️ Drone {DRONE_ID} reversing direction."
        )


# ============================================================
# RECEIVE GPS DATA
# ============================================================

def receive_gps():

    receiver = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    # Allows the program to restart quickly
    receiver.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    receiver.bind(
        (NETWORK_IP, MY_PORT)
    )

    print(
        f"🟩 Drone {DRONE_ID} receiver "
        f"listening on "
        f"{NETWORK_IP}:{MY_PORT}"
    )


    while True:

        try:

            data, address = receiver.recvfrom(4096)

            packet = json.loads(
                data.decode()
            )


            # Ignore our own packets
            if packet["drone_id"] == DRONE_ID:

                continue


            print()
            print("📡 GPS RECEIVED")
            print("----------------------------")

            print(
                f"From Drone : "
                f"{packet['drone_id']}"
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


        except json.JSONDecodeError:

            print(
                "⚠️ Invalid GPS packet received."
            )


        except Exception as error:

            print(
                f"⚠️ Receiver error: {error}"
            )


# ============================================================
# SEND GPS DATA
# ============================================================

def send_gps():

    sender = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    print(
        f"🟦 Drone {DRONE_ID} sender started"
    )

    print(
        f"GPS: "
        f"{my_gps['latitude']:.6f}, "
        f"{my_gps['longitude']:.6f}, "
        f"{my_gps['altitude']:.1f} m"
    )


    while True:

        try:

            # Move drone
            update_position()


            # Create GPS packet
            packet = {

                "drone_id":
                    DRONE_ID,

                "latitude":
                    my_gps["latitude"],

                "longitude":
                    my_gps["longitude"],

                "altitude":
                    my_gps["altitude"],

                "timestamp":
                    time.time()
            }


            # Convert GPS packet to JSON
            data = json.dumps(packet).encode()


            # Send to all other drones
            for target_drone, target_port in OTHER_DRONES.items():

                sender.sendto(
                    data,
                    (
                        NETWORK_IP,
                        target_port
                    )
                )


                print(
                    f"📤 Drone {DRONE_ID} → "
                    f"Drone {target_drone} | "
                    f"GPS: "
                    f"{my_gps['latitude']:.6f}, "
                    f"{my_gps['longitude']:.6f}, "
                    f"{my_gps['altitude']:.1f} m"
                )


            # Wait before next GPS update
            time.sleep(
                UPDATE_INTERVAL
            )


        except KeyboardInterrupt:

            print()
            print(
                f"🛑 Drone {DRONE_ID} stopped."
            )

            sender.close()

            break


        except Exception as error:

            print(
                f"⚠️ Sender error: {error}"
            )

            time.sleep(1)


# ============================================================
# PROGRAM START
# ============================================================

print()

print("========================================")

print(
    f"🚁 AEROCUE SEARCH DRONE {DRONE_ID}"
)

print("========================================")

print(
    f"Network IP     : {NETWORK_IP}"
)

print(
    f"Own GPS        : "
    f"{my_gps['latitude']:.6f}, "
    f"{my_gps['longitude']:.6f}, "
    f"{my_gps['altitude']:.1f} m"
)

print(
    f"Search range   : "
    f"{START_LONGITUDE:.6f} → "
    f"{END_LONGITUDE:.6f}"
)

print(
    f"Listening on   : "
    f"{NETWORK_IP}:{MY_PORT}"
)

print(
    f"Communicating with: "
    f"Drone {list(OTHER_DRONES.keys())}"
)

print("========================================")

print()


# ============================================================
# START RECEIVER
# ============================================================

receiver_thread = threading.Thread(
    target=receive_gps,
    daemon=True
)

receiver_thread.start()


# ============================================================
# START SENDER
# ============================================================

send_gps()
