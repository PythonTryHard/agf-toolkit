import os
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import adbutils
import cv2
import numpy as np
import requests
from adbutils import adb
from loguru import logger
from tqdm import tqdm


def _monkeypatch_screenshot(self: adbutils.AdbDevice) -> np.ndarray[int, np.dtype[np.generic]]:
    """
    Monkey patch for adbutils.AdbDevice.screenshot()

    Based on https://github.com/openatx/adbutils/pull/78, replacing PIL with cv2, and using 3.8+ syntax.
    """
    conn = self.shell(["screencap", "-p"], stream=True)
    raw_png = b""
    while chunk := conn.read(4096):
        raw_png += chunk

    img = cv2.imdecode(np.frombuffer(raw_png, np.uint8), 1)
    return img


adbutils.AdbDevice.screenshot = _monkeypatch_screenshot


ADB_DOWNLOAD_PATH = Path("~/.agf_toolkit").expanduser()
ADB_DOWNLOAD_FNAME = ADB_DOWNLOAD_PATH / "platform-tools.zip"
ADB_DOWNLOAD_EXECUTABLE = ADB_DOWNLOAD_PATH / "platform-tools" / "adb"

ADB = shutil.which("adb") or ADB_DOWNLOAD_EXECUTABLE

if not os.path.exists(ADB):
    logger.info("ADB not found. Downloading...")

    match platform.system():
        case "Windows":
            ADB_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        case "Linux":
            ADB_URL = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
        case "Darwin":
            ADB_URL = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
        case _:
            logger.critical("Unsupported platform! Please install adb manually!")
            sys.exit(1)

    if not ADB_DOWNLOAD_PATH.exists():
        os.mkdir(ADB_DOWNLOAD_PATH)

    resp = requests.get(ADB_URL, stream=True, timeout=15.0)
    total = int(resp.headers.get("content-length", 0))
    with open(ADB_DOWNLOAD_FNAME, "wb") as file, tqdm(
        desc=ADB_DOWNLOAD_FNAME.name,
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

    logger.info(f"Extracting ADB to {ADB_DOWNLOAD_PATH}")
    with ZipFile(ADB_DOWNLOAD_FNAME) as zf:
        zf.extractall(ADB_DOWNLOAD_PATH)
        st = os.stat(ADB)
        os.chmod(ADB, st.st_mode | stat.S_IEXEC)

    os.remove(ADB_DOWNLOAD_FNAME)


logger.info("Starting ADB server...")
subprocess.run([ADB, "start-server"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Connect to device over network if needed
if all([ip := os.environ.get("IP"), port := os.environ.get("PORT")]):  # Dirty null check
    logger.info("Connecting to device over network.")
    try:
        adb.connect(f"{ip}:{port}", timeout=5.0)  # Should be more than enough
    except adbutils.errors.AdbTimeout:
        logger.critical("Timeout! Failed to connect to device over network!")
        sys.exit(1)

match len(device_list := adb.device_list()):
    case 0:
        logger.critical("No devices found!")
        sys.exit(1)
    case 1:
        DEVICE = device_list[0]
    case _:
        print("Select your device: ")
        for i, d in enumerate(device_list):
            print(f"{i :<2}: {d.serial}")

        print("(Enter a number (1 - {len(device_list)})): ", end="")
        while not ((choice := input()).isnumeric() and int(choice) in range(1, len(device_list) + 1)):
            print("Invalid input! Please try again: ", end="")

        DEVICE = device_list[int(choice) - 1]


def screencap() -> np.ndarray[int, np.dtype[np.generic]]:
    """Take a screenshot from the connected device."""
    logger.info("Taking screenshot.")
    return DEVICE.screenshot()
