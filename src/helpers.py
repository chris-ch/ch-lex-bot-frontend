import time


def string_to_stream(input_string, delay=0.05):
    for word in input_string.split():
        yield word + " "
        time.sleep(delay)
