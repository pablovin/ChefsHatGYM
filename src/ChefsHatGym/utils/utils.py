import threading
import logging
import os

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y %m %d %H:%M:%S",
    level=logging.INFO,
)


def get_logger(logger_name, log_directory, log_name):
    # Creating logger
    logger = logging.getLogger(logger_name)

    file_handler = logging.FileHandler(
        os.path.join(log_directory, log_name),
        mode="w",
        encoding="utf-8",
    )

    # logger.addHandler(
    #     logging.FileHandler(
    #         os.path.join(log_directory, "rom_log.log"),
    #         mode="w",
    #         encoding="utf-8",
    #     )
    # )

    # Create a formatter with the specified format and date format
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y %m %d %H:%M:%S"
    )

    # Assign the formatter to the handler
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

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
