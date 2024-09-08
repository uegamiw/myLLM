from models.database_manager import DatabaseManager
from views.history_panel import HistoryPanel

# Not implemented yet

class history_controller:

    def __init__(self, db_manager:DatabaseManager, h_panel: HistoryPanel) -> None:
        self.db_manager = db_manager
        self.h_panel = h_panel

        
