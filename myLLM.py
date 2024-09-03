import os
import sys
from logging import getLogger, Formatter, DEBUG, INFO, StreamHandler
from PySide6.QtWidgets import (
    QApplication,
)
from config_manager import ConfigManager
from gpt_app import GPTApp
from api_client_manager import APIClientManager
from setting import json_path, log_path, log_backup_count, log_max_bytes

def main():
    file_logging = True

    # disable the console window on MacOS
    if sys.platform == 'darwin':
        file_logging = False
        os.environ['QT_MAC_WANTS_LAYER'] = '1'
        os.environ['QT_ENABLE_GLYPH_CACHE_WORKAROUND'] = '1'

    # Initialize the logger
    os.makedirs(log_path.parent, exist_ok=True)
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    sh = StreamHandler()
    sh.setLevel(INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if file_logging:
        from logging.handlers import RotatingFileHandler
        fh = RotatingFileHandler(
            log_path, maxBytes=log_max_bytes, backupCount=log_backup_count
        )
        fh.setLevel(INFO)
        fh.setFormatter(formatter)  # Add this line to set the formatter
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
