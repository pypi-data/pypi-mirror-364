import os
import logging
import httpx


def healthchecks(suffix: str = ""):
    env_name = "HEALTHCHECKS_URL"
    url = os.environ.get(env_name)
    if url is None:
        logging.warning(f"Missing {env_name}. Skipping healthchecks")
        return
    url = url + suffix
    httpx.get(url)
