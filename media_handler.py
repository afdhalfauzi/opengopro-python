import sys
import json
import argparse
from typing import Dict, Any

import requests

from tutorial_modules import GOPRO_BASE_URL, logger


def get_media_list() -> Dict[str, Any]:
    """Read the media list from the camera and return as JSON

    Returns:
        Dict[str, Any]: complete media list as JSON
    """
    # Build the HTTP GET request
    url = GOPRO_BASE_URL + "/gopro/media/list"
    logger.info(f"Getting the media list: sending {url}")

    # Send the GET request and retrieve the response
    response = requests.get(url, timeout=10)
    # Check for errors (if an error is found, an exception will be raised)
    response.raise_for_status()
    logger.info("Command sent successfully")
    # Log response as json
    logger.info(f"Response: {json.dumps(response.json(), indent=4)}")

    return response.json()