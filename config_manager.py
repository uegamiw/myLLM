import json
from pathlib import Path
from logging import Logger

class ConfigManager:
    def __init__(self, json_path: Path, logger: Logger) -> None:
        self.json_path = json_path
        self.logger = logger
        self.config = self.load_config()

    def load_config(self) -> dict:
        try:
            with open(self.json_path, "r") as f:
                config = json.load(f)
                self.logger.info(f"config.json loaded")
        except FileNotFoundError as e:
            self.logger.critical(f"FileNotFoundError: {e}")
            config = {}
        except json.JSONDecodeError as e:
            self.logger.critical(f"JSONDecodeError: {e}")
            config = {}
        except Exception as e:
            self.logger.critical(f"Unexpected Error: {e}")
            config = {}
        return config