import logging
import time


def string_to_stream(input_string, delay=0.05):
    for word in input_string.split():
        yield word + " "
        time.sleep(delay)


def setup_logging_levels():
    """
    Basic logging setup.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
