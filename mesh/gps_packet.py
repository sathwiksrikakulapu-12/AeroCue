import json
import time


def create_gps_packet(drone_id, latitude, longitude, altitude):
    packet = {
        "drone_id": drone_id,
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude,
        "timestamp": time.time()
    }

    return packet


def encode_packet(packet):
    return json.dumps(packet)


def decode_packet(data):
    return json.loads(data)
