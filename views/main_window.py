from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from views.menu_bar import MenuBar
from views.history_panel import HistoryPanel
from views.center_panel import CenterPanel
from views.right_panel import RightPanel
from models.config_manager import Config
from models.api_client_manager import APIClientManager
from models.database_manager import DatabaseManager
from utils.setting import window_title, spacing, window_geometry

class MainWindow(QMainWindow):
    def __init__(
        self, config:Config, clients: APIClientManager, db: DatabaseManager,  logger
    ):
        super().__init__()
        self.config = config
        self.clients = clients
        self.prompts = self.config.prompts
        self.db = db
        self.logger = logger

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(window_title)
        self.setGeometry(*window_geometry)

        # Create a central widget and set it
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(spacing)

        # Create a splitter
        splitter = QSplitter(Qt.Horizontal)

        # History panel
        self.history_panel = HistoryPanel(self.db, self.logger)
        # self.history_panel.item_selected.connect(self.show_history_item)

        # Center panel
        self.center_panel = CenterPanel(
            self.config, self.logger
        )

        self.right_panel = RightPanel(
            self.config, self.clients, self.history_panel, self.logger
        )

        # Add panels to the splitter
        splitter.addWidget(self.history_panel)
        splitter.addWidget(self.center_panel)
        splitter.addWidget(self.right_panel)

        # Set initial sizes (optional)
        splitter.setSizes([350, 600, 200])  # Example: history panel 300px, main panel 900px

        main_layout.addWidget(splitter)

        # Menu bar
        self.menubar = MenuBar(self, self.prompts, self.logger)
        self.setMenuBar(self.menubar)

        self.center_panel.input_panel.textarea.setFocus()

    def show_history_item(self, item):
        self.center_panel.input_panel.set_text(item["query"])
        self.center_panel.output_area.set_text(item["response"])
        self.center_panel.model_selection_panel.set_selected_model(item["model"])

    def closeEvent(self, event):
        self.db.close()
        self.logger.info("App Closed")
        event.accept()