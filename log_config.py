import logging

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("app.log")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a logger
logger.setLevel(logging.DEBUG)

# Create a file handler and set the log level
file_handler.setLevel(logging.DEBUG)

# Create a console handler and set the log level
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
