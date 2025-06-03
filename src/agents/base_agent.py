import os
import logging


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


class BaseAgent:

    def __init__(self, name, log_directory=""):
        self.name = name
        self.log_directory = log_directory

        self.this_log_folder = os.path.join(
            os.path.abspath(log_directory), "agents", self.name
        )
        if log_directory != "":
            if not os.path.exists(self.this_log_folder):
                os.makedirs(self.this_log_folder)

        self.logger = get_logger(
            f"PLAYER_{self.name}",
            self.this_log_folder,
            f"PLAYER_{self.name}.log",
            False,
            True,
        )

        self.log("---------------------------")
        self.log(f"Player {self.name} created!")
        self.log(f"  - Agent folder: {self.this_log_folder}")
        self.log("---------------------------")

    def log(self, message):
        """Log a certain message, if the verbose is True

        Args:
            message (_type_): _description_
        """
        self.logger.info(f"[Agent {self.name}]:  {message}")

    def update_game_start(self, payload):
        pass

    def update_game_over(self, payload):
        pass

    def update_new_hand(self, payload):
        pass

    def update_new_roles(self, payload):
        pass

    def update_food_fight(self, payload):
        pass

    def update_dinner_served(self, payload):
        pass

    def update_hand_after_exchange(self, payload):
        pass

    def update_start_match(self, payload):
        pass

    def update_match_over(self, payload):
        pass

    def update_player_action(self, payload):
        pass

    def update_pizza_declared(self, payload):
        pass

    # ==== Synchronous stubs (for user to override) Requests ====

    def request_cards_to_exchange(self, info):
        pass

    def request_special_action(self, info):
        pass

    def request_action(self, info):
        pass
