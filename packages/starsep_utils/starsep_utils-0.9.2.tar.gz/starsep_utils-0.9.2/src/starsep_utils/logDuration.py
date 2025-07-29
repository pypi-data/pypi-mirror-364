import logging

from funcy import log_durations

logDuration = log_durations(lambda msg: logging.info("⌛ " + msg))
