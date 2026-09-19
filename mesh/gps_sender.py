import socket
import time

from gps_packet import create_gps_packet, encode_packet


RECEIVER_IP = "127.0.0.1"
RECEIVER_PORT = 5000

DRONE_ID = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("GPS Sender started...")
print(f"Sending GPS data to {RECEIVER_IP}:{RECEIVER_PORT}")

while True:

    packet = create_gps_packet(
        drone_id=DRONE_ID,
        latitude=13.082680,
        longitude=80.270718,
        altitude=120.5
    )

    data = encode_packet(packet)

    sock.sendto(
        data.encode(),
        (RECEIVER_IP, RECEIVER_PORT)
    )

    print(
        f"Sent GPS: "
        f"Drone {DRONE_ID} | "
        f"Lat {packet['latitude']} | "
        f"Lon {packet['longitude']} | "
        f"Alt {packet['altitude']} m"
    )

    time.sleep(2)
