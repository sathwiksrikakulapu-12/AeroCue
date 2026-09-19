import socket
import json


HOST = "0.0.0.0"
PORT = 5000


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print(f"GPS Receiver listening on UDP port {PORT}...")

while True:
    data, address = server.recvfrom(4096)

    packet = json.loads(data.decode())

    print("\n--- GPS DATA RECEIVED ---")
    print(f"From: {address[0]}:{address[1]}")
    print(f"Drone ID: {packet['drone_id']}")
    print(f"Latitude: {packet['latitude']}")
    print(f"Longitude: {packet['longitude']}")
    print(f"Altitude: {packet['altitude']} m")
    print(f"Timestamp: {packet['timestamp']}")
