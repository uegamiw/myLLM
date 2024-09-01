import os
import sys
from logging import getLogger, Formatter, DEBUG, INFO, StreamHandler
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import (
    QApplication,
)
from config_manager import ConfigManager
from gpt_app import GPTApp
from api_client_manager import APIClientManager
from setting import json_path, log_path, log_backup_count, log_max_bytes

def main():

    # Initialize the logger
    os.makedirs(log_path.parent, exist_ok=True)
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    sh = StreamHandler()
    fh = RotatingFileHandler(
        log_path, maxBytes=log_max_bytes, backupCount=log_backup_count
    )
    sh.setLevel(INFO)
    fh.setLevel(INFO)
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    sh.setFormatter(formatter)
    fh.setFormatter(formatter)  # Add this line to set the formatter
    logger.addHandler(sh)
    logger.addHandler(fh)

    logger.info("App started")

    config_manager = ConfigManager(json_path, logger)
    config = config_manager.config

    api_clients_manager = APIClientManager(logger)

    api_clients_manager.get_openai_client()
    api_clients_manager.get_anthropic_client()

    app = QApplication(sys.argv)
    llm_app = GPTApp(config_manager, api_clients_manager, logger)

    llm_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
