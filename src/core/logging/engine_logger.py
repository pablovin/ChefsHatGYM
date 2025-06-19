# core/room_logger.py

import logging
import os
import datetime


class EngineLogger:
    def __init__(
        self,
        room_name,
        timestamp,
        player_names,
        config,
        save_logs=True,
        output_folder="outputs",
    ):
        self.save_logs = save_logs
        self.room_name = room_name
        self.timestamp = timestamp

        self.output_folder = output_folder
        self.player_names = player_names
        self.config = config

        if not save_logs:
            self._noop_all()
            return

        logs_folder = os.path.join(self.output_folder, "logs")
        os.makedirs(logs_folder, exist_ok=True)

        self.logger = self._init_logger(
            "engine", os.path.join(logs_folder, "engine.log")
        )
        self._log_game_start()

    def _noop_all(self):
        """Disable all logging methods when logs are not saved."""
        self.engine_log = lambda message: None

    def _init_logger(self, name, filepath):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        handler = (
            logging.FileHandler(filepath, mode="w")
            if filepath
            else logging.NullHandler()
        )

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _log_game_start(self):
        ascii_banner = r"""
    _____ _           __ _       _   _         _
    / ____| |         / _(_)     | | (_)       | |
    | |    | |__   ___| |_ _  __ _| |_ _  ___ __| |___
    | |    | '_ \ / _ \  _| |/ _` | __| |/ __/ _` / __|
    | |____| | | |  __/ | | | (_| | |_| | (_| (_| \__ \
    \_____|_| |_|\___|_| |_|\__,_|\__|_|\___\__,_|___/
            """
        self.logger and self.logger.info(ascii_banner)
        self.logger and self.logger.info("Starting a new Chef's Hat Game!")
        self.logger and self.logger.info("Game rules:")
        self.logger and self.logger.info(f"- Max matches: {self.config['max_matches']}")
        self.logger and self.logger.info(
            f"- Max rounds per match: {self.config['max_rounds'] if self.config['max_rounds'] else 'Unlimited'}"
        )
        self.logger and self.logger.info(
            f"- Max score to win: {self.config['max_score'] if self.config['max_score'] else 'None'}"
        )

        player_dict = {index: p for index, p in enumerate(self.player_names)}
        self.logger and self.logger.info(f"Players: {player_dict}")

        self.now = datetime.datetime.now()
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger and self.logger.info(f"Game started at: {start_time}")

    def engine_log(self, message):
        self.logger.info(message)

    # def log_game_start(self):
    #     self.logger.info("\n=== GAME STARTED ===")

    # def log_match_start(self, match_number):
    #     self.logger.info(f"\n--- MATCH {match_number} STARTED ---")

    # def log_match_end(self):
    #     self.logger.info("\n--- MATCH ENDED ---")

    # def log_game_end(self, final_scores):
    #     self.logger.info("\n=== GAME ENDED ===")
    #     self.logger.info(f"Final scores: {final_scores}")

    # def log_notify(self, recipients, method, args):
    #     if isinstance(recipients, list):
    #         for r in recipients:
    #             self.logger.info(f"Notify -> {r} | method={method} | args={args}")
    #     else:
    #         self.logger.info(f"Notify -> {recipients} | method={method} | args={args}")

    # def log_request(self, agent_name, method, args, response):
    #     self.logger.info(
    #         f"Request -> {agent_name} | method={method} | args={args} | response={response}"
    #     )

    # def log_action_info(self, agent_name, action_info):
    #     self.logger.info(f"Notify {agent_name} of action: {action_info}")

    # def log_pizza(self, player_name, round_number):
    #     self.logger.info(
    #         f"Round Over - Pizza declared by {player_name} | Round={round_number}"
    #     )
