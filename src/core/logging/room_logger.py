# core/room_logger.py

import logging
import os


class RoomLogger:
    def __init__(
        self,
        room_name,
        timestamp,
        config,
        save_logs=True,
        output_folder="outputs",
        local=True,
    ):
        self.save_logs = save_logs
        self.room_name = room_name
        self.timestamp = timestamp
        self.output_folder = output_folder
        self.config = config
        self.local = local

        if not save_logs:
            self._noop_all()
            return

        logs_folder = os.path.join(self.output_folder, "logs")
        os.makedirs(logs_folder, exist_ok=True)

        self.logger = self._init_logger("room", os.path.join(logs_folder, "room.log"))
        self.log_room_intro()

    def _noop_all(self):
        self.log_room_intro = lambda: None
        self.room_log = lambda message: None

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

    def log_room_intro(self):
        header = """
        =======================================
                 ___ ___ ___ _  _   _   
                | __|_ _|_ _| \| | /_\  
                | _| | | | || .` |/ _ \ 
                |_| |___|___|_|\_/_/ \_\
              Welcome to the Chef's Hat Room
        =======================================
        """
        self.logger.info(header)
        self.logger.info(f"Room Name: {self.room_name}")
        self.logger.info(f"Creation Date: {self.timestamp}")
        self.logger.info(f"Local Room: {self.local}")
        self.logger.info("Game Rules:")
        for key, value in self.config.items():
            self.logger.info(f"- {key}={value}")

    def room_log(self, message):
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
