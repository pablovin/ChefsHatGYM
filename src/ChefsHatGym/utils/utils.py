import threading
import logging
import os

# logging.basicConfig(
#     format="%(asctime)s %(levelname)-8s %(message)s",
#     datefmt="%Y %m %d %H:%M:%S",
#     level=logging.INFO,
# )


def get_logger(logger_name, log_directory, log_name, verbose_console, verbose_log):

    # Creating logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    # Create a formatter with the specified format and date format
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y %m %d %H:%M:%S"
    )

    if verbose_log:
        file_handler = logging.FileHandler(
            os.path.join(log_directory, log_name),
            mode="w",
            encoding="utf-8",
        )

        # Assign the formatter to the handler
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)

    if verbose_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger


def threaded(fn):
    """A wrapper for a threaded function

    Args:
        fn (function): function to be threaded
    """

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper
