import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)