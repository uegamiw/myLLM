import os
import sys
from logging import getLogger, Formatter, INFO, StreamHandler
from PySide6.QtWidgets import (
    QApplication,
)
from models.config_manager import ConfigManager
from controllers.status_bar_controller import StatusBarController
from views.main_window import MainWindow
from models.api_client_manager import APIClientManager
from utils.setting import json_path, log_path, log_backup_count, log_max_bytes, db_path

from controllers.main_controller import MainController
from models.database_manager import DatabaseManager


def main():
    file_logging = True

    # disable the console window on MacOS
    if sys.platform == "darwin":
        file_logging = False
        os.environ["QT_MAC_WANTS_LAYER"] = "1"
        os.environ["QT_ENABLE_GLYPH_CACHE_WORKAROUND"] = "1"

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

    app = QApplication(sys.argv)
    db = DatabaseManager(logger, db_path)

    main_window = MainWindow(config, api_clients_manager, db, logger)
    status_bar_controller = StatusBarController(main_window, logger)

    main_controller = MainController(
        main_window.center_panel,
        main_window.menubar,
        main_window.history_panel,
        main_window.right_panel,
        api_clients_manager,
        db,
        config,
        status_bar_controller,
        logger
        )


    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
