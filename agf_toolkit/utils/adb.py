import os
import sys
from io import BytesIO

import cv2
import numpy as np
from loguru import logger
from ppadb.client import Client
from ppadb.device import Device


def get_adb_client() -> Client:
    """Get an ADB client."""
    ip = os.environ.get("ADB_IP")
    port = int(os.environ.get("ADB_PORT"))

    logger.info(f"Attempting to connect to ADB server @ {ip}:{port}")
    ADB_CLIENT = Client(host=ip, port=port)

    try:
        ADB_CLIENT.create_connection()
    except RuntimeError as e:
        if "Is adb running on your computer?" in e.args[0]:
            logger.error(
                f"Could not connect to local ADB @ {ip}:{port}! "
                "Make sure ADB is running on your computer by running 'adb start-server' first!"
            )
            if __name__ == "__main__":
                sys.exit(1)

        else:
            raise e

    logger.info("Connected to ADB.")
    return ADB_CLIENT


def get_device(client: Client) -> Device:
    """Attempt to connect to the device running Artery Gear: Fusion."""
    logger.info("Attempting to connect to device.")
    match os.environ.get("CONNECTION_TYPE").lower():
        case "usb":
            if (device := client.device(os.environ.get("IDENTIFIER"))) is not None:
                logger.info("Connected to device.")
                return device

        case "ip":
            ip, port = os.environ.get("IDENTIFIER"), int(os.environ.get("PORT"))
            if client.remote_connect(host=ip, port=port):
                device = list(filter(lambda x: x.serial == f"{ip}:{port}", client.devices()))[0]
                logger.info("Connected to device.")
                return device

        case _:
            logger.error("Invalid connection type specified in .env!")
            sys.exit(1)

    # Since all code paths either return or exit, this should be reached when device is not found.
    logger.error("Could not find/connect to device! Please check your '.env' file and try again!")
    if __name__ == "__main__":
        sys.exit(1)


def screencap(device: Device) -> cv2.Mat:
    """Take a screenshot and convert to OpenCV-compatible."""
    logger.info("Taking screenshot.")
    raw_byte = BytesIO(device.screencap())  # PNG
    logger.info("Screenshot received. Converting to OpenCV BGR image.")
    img = cv2.imdecode(np.frombuffer(raw_byte.read(), np.uint8), 1)
    return img
