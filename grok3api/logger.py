import logging

log_level = logging.WARNING
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)