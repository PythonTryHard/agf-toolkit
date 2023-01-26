# pylint: disable=invalid-name,import-outside-toplevel
import concurrent.futures
import hashlib
import json
import os
import sys
from datetime import datetime
from itertools import repeat
from pathlib import Path

try:
    import typer
except ImportError:
    print("You are missing dependencies for the command-line interface (CLI)! Refer to docs for instruction!")
    sys.exit(1)
from loguru import logger
from tqdm import tqdm

from agf_toolkit import DATA_DIR

CALIBRATION_FILE = (DATA_DIR / "calibration_result.txt").expanduser()
PARSED_RESULTS_FILE = (DATA_DIR / "parsed_results.json").expanduser()

DATA_DIR.mkdir(parents=True, exist_ok=True)

app = typer.Typer(no_args_is_help=True, add_completion=False)


def get_file_hash(file_path):
    """Calculate the sha256 hash of a file"""
    sha256_hash = hashlib.sha3_256()
    with open(file_path, "rb") as fp:
        for byte_block in iter(lambda: fp.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@app.callback()
def global_options(debug: bool = False):
    """Global options for the CLI"""
    if debug:
        os.environ["LOGURU_LEVEL"] = "DEBUG"
    else:
        os.environ["LOGURU_LEVEL"] = "INFO"


@app.command()
def calibrate(
    image_path: str = typer.Option("", help="Path to the image to calibrate. Leave blank to connect using ADB."),
):
    """
    Calibrate the toolkit before parsing (default: using Android Debug Bridge).

    You can also provide an image path to calibrate the toolkit with an existing screenshot.
    """
    logger.info("Loading modules, please wait...")
    from agf_toolkit.processor.calibration import auto_calibrate_scale

    if image_path:
        import cv2

        image = cv2.imread(image_path)
    else:
        from agf_toolkit.utils import adb

        image = adb.screencap()

    scale = auto_calibrate_scale(image)
    with open(CALIBRATION_FILE.expanduser(), "x", encoding="utf-8") as fp:
        fp.write(str(scale))

    logger.info(f"Calibration complete! Scale: {scale}. This value has been saved to {CALIBRATION_FILE}.")


@app.command()
def parse_files(
    file_paths: list[str] = typer.Argument(..., help="Files you wants to parse."),
    workers: int = typer.Option(0, help="Number of parallel workers to use for parsing."),
):
    """
    Parse screenshots. Multiple files can be provided to parse at once.

    You can specify the number of parallel workers to use for parsing.
    """
    logger.info("Loading modules, please wait...")
    from agf_toolkit.processor.utils import parallel_parse_screenshot

    # Ensure user has calibrated the toolkit
    if not os.path.exists(CALIBRATION_FILE):
        logger.critical("You have not calibrated the toolkit yet! Please run 'agf_toolkit calibrate --help' first!")
        sys.exit(1)

    with open(CALIBRATION_FILE, encoding="utf-8") as fp:
        scale = float(fp.read())

    # Load in pre-existing results
    if not os.path.exists(PARSED_RESULTS_FILE):
        with open(PARSED_RESULTS_FILE, "x", encoding="utf-8") as fp:
            fp.write("{}")
    with open(PARSED_RESULTS_FILE, encoding="utf-8") as fp:
        parsed_results = json.load(fp)

    # Skip files that have already been parsed
    sha256_list, file_list = zip(
        *[(sha256, file) for file in file_paths if (sha256 := get_file_hash(file)) not in parsed_results]
    )

    # Set up loguru to interop with tqdm
    logger.remove()
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True, enqueue=True)

    # Start parsing
    with tqdm(total=len(file_list)) as pbar:
        with concurrent.futures.ProcessPoolExecutor(max_workers=max(workers, 1)) as executor:
            futures = {
                executor.submit(parallel_parse_screenshot, *arg): arg for arg in list(zip(file_list, repeat(scale)))
            }
            result = []

            for future in concurrent.futures.as_completed(futures):
                result.append(
                    {"file_name": str(Path(futures[future][0]).absolute()), "result": future.result().encode()}
                )
                pbar.update(1)

    result_dict = dict(zip(sha256_list, result))

    # Store the parsed gear back
    parsed_results.update(result_dict)
    with open(PARSED_RESULTS_FILE, "w", encoding="utf-8") as fp:
        json.dump(parsed_results, fp, indent=4)


@app.command()
def parse_screen():
    """
    Start a live parsing session using Android Debug Bridge.
    """
    logger.info("Loading modules, please wait...")
    from agf_toolkit.processor.image import rescale
    from agf_toolkit.processor.utils import parse_screenshot
    from agf_toolkit.utils import adb

    # Ensure user has calibrated the toolkit
    if not os.path.exists(CALIBRATION_FILE):
        logger.critical("You have not calibrated the toolkit yet! Please run 'agf_toolkit calibrate --help' first!")
        sys.exit(1)

    with open(CALIBRATION_FILE, encoding="utf-8") as fp:
        scale = float(fp.read())

    logger.info("Starting live parsing session...")
    logger.warning("Press Enter to initiate a screenshot and parsing.")
    logger.warning("Press Ctrl+C to exit.")
    try:
        with open(PARSED_RESULTS_FILE, encoding="utf-8") as fp:
            parsed_results = json.load(fp)

        while True:
            input("Press Enter to continue...")
            image = adb.screencap()
            result = parse_screenshot(rescale(image, scale)).encode()

            # Store the parsed gear back
            sha256 = hashlib.sha3_256(image).hexdigest()
            file_name = f"live_{datetime.now()}"
            parsed_results.update({sha256: {"file_name": file_name, "result": result}})
            with open(PARSED_RESULTS_FILE, encoding="utf-8") as fp:
                json.dump(parsed_results, fp, indent=4)

            logger.info(f"Result saved to {file_name}!")

    except KeyboardInterrupt:
        logger.info("Exiting...")


app()
