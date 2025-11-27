import os
import logging
import asyncio
import json

try:
    import websockets
except Exception:  # pragma: no cover - optional for local tests
    websockets = None


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

    if not verbose_console and not verbose_log:
        logger.addHandler(logging.NullHandler())

    logger.propagate = False

    return logger


class BaseAgent:

    def __init__(
        self,
        name,
        log_directory="",
        verbose_console=True,
        run_remote=False,
        host="localhost",
        port=8765,
        room_name="room",
        room_password="password",
    ):
        self.name = name
        self.log_directory = log_directory

        self.run_remote = run_remote
        self.remote_host = host
        self.remote_port = port
        self.remote_room_name = room_name
        self.remote_room_password = room_password
        self.ws = None

        self.this_log_folder = os.path.join(
            os.path.abspath(log_directory), "agents", self.name
        )
        print(f"Log_directory: {log_directory}")
        verbose_log = False
        if log_directory != "":
            os.makedirs(self.this_log_folder, exist_ok=True)
            verbose_log = True

        self.logger = get_logger(
            f"PLAYER_{self.name}",
            self.this_log_folder,
            f"PLAYER_{self.name}.log",
            verbose_console,
            verbose_log,
        )

        if not verbose_console and not verbose_log:
            self.log = lambda message: None

        self.log("---------------------------")
        self.log(f"Player {self.name} created!")
        self.log(f"  - Agent folder: {self.this_log_folder}")
        self.log(f"Running mode: {'REMOTE' if self.run_remote else 'LOCAL'}")
        if self.run_remote:
            self.log(
                f"Remote target ws://{self.remote_host}:{self.remote_port} room={self.remote_room_name}"
            )
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

    # === Remote support ===
    async def connect_remote(self):
        if websockets is None:
            raise ImportError("websockets package is required for remote mode")

        uri = f"ws://{self.remote_host}:{self.remote_port}"
        while True:
            try:
                self.ws = await websockets.connect(uri)
                await self.ws.send(
                    json.dumps(
                        {
                            "player_name": self.name,
                            "password": self.remote_room_password,
                            "room_name": self.remote_room_name,
                        }
                    )
                )
                resp = json.loads(await self.ws.recv())
                if resp.get("status") != "connected":
                    raise RuntimeError(resp.get("error", "Connection refused"))
                break
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.log(f"Connection failed: {e}. Retrying...")
                await asyncio.sleep(1)

    async def remote_loop(self):
        try:
            while True:
                if not self.ws:
                    await self.connect_remote()
                try:
                    msg = await self.ws.recv()
                except websockets.exceptions.ConnectionClosed:
                    self.ws = None
                    continue
                data = json.loads(msg)
                mtype = data.get("type")
                raw_payload = data.get("payload", "{}")

                # Deserialize the payload string into a Python dict
                print(f"Raw Payload: {raw_payload}")
                payload = json.loads(raw_payload)
                if mtype.startswith("request_"):
                    method = getattr(self, mtype)
                    result = method(payload)
                    await self.ws.send(json.dumps({"result": result}))
                else:
                    method = getattr(self, mtype, None)
                    if method:
                        method(payload)
                if mtype == "update_game_over":
                    break
        except asyncio.CancelledError:
            if self.ws:
                await self.ws.close()
            raise
        if self.ws:
            await self.ws.close()
