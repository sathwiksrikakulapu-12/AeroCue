import socket
import json
import threading
import time


PORT = 5000

DRONE_ID = 1

MY_LATITUDE = 13.082680
MY_LONGITUDE = 80.270718
MY_ALTITUDE = 120.5


def receive_gps():
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind(("127.0.0.1", PORT))

    print(f"Drone {DRONE_ID} receiver listening on port {PORT}...")

    while True:
        data, address = receiver.recvfrom(4096)

        packet = json.loads(data.decode())

        # Ignore our own packets
        if packet["drone_id"] == DRONE_ID:
            continue

        print("\n--- GPS DATA FROM OTHER DRONE ---")
        print(f"Drone ID: {packet['drone_id']}")
        print(f"Latitude: {packet['latitude']}")
        print(f"Longitude: {packet['longitude']}")
        print(f"Altitude: {packet['altitude']} m")


def send_gps():
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        packet = {
            "drone_id": DRONE_ID,
            "latitude": MY_LATITUDE,
            "longitude": MY_LONGITUDE,
            "altitude": MY_ALTITUDE,
            "timestamp": time.time()
        }

        data = json.dumps(packet).encode()

        sender.sendto(data, ("127.0.0.1", PORT))

        print(
            f"Sent GPS | "
            f"Drone {DRONE_ID} | "
            f"{MY_LATITUDE}, {MY_LONGITUDE} | "
            f"{MY_ALTITUDE} m"
        )

        time.sleep(2)


receiver_thread = threading.Thread(
    target=receive_gps,
    daemon=True
)

receiver_thread.start()

send_gps()
