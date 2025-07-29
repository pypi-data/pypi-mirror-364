from typing import Any, Callable, Dict

import requests


def make_request(method: str, url: str, get_headers: Callable[[], Dict[str, str]], json=None, logger=None) -> Dict[str, Any]:
    headers = get_headers()
    response = requests.request(method, url, headers=headers, json=json)
    response.raise_for_status()

    if logger:
        logger.debug("Status code: %s", response.status_code)
        logger.debug("Response: %s", response.text)

    if response.text:
        return response.json()
    return {}