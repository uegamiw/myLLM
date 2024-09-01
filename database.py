import sqlite3
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject

class DatabaseManager(QObject):
    def __init__(self,logger, db_path):
        super().__init__()
        self.logger = logger
        self.db_name = Path(db_path)
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        # Handle the exception if the self_db_name is not found)
        
        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {e}")

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            datetime TEXT NOT NULL,
            model TEXT NOT NULL
        )
        '''
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error creating table: {e}")

    def insert_history(self, query, response, model):
        insert_query = '''
        INSERT INTO history (query, response, datetime, model)
        VALUES (?, ?, ?, ?)
        '''
        current_time = datetime.now().isoformat()
        try:
            self.cursor.execute(insert_query, (query, response, current_time, model))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting data: {e}")

    # fetch latest n data from the database in descending order
    # return a list of dictionaries
    def get_n_history(self, n) -> list:
        select_query = "SELECT * FROM history ORDER BY datetime DESC LIMIT ?"
        try:
            self.cursor.execute(select_query, (n,))
            items = []
            for item in self.cursor.fetchall():

                query_min_length = min(len(item[1]), 10)
                response_min_length = min(len(item[2]), 10)

                items.append({
                    "id": item[0],
                    "query": item[1],#[0:query_min_length],
                    "response": item[2],#[0:response_min_length],
                    "datetime": item[3],
                    "model": item[4]
                })
            return items

        except sqlite3.Error as e:
            self.logger.error(f"Error fetching data: {e}")
            return []
    
    # function to fetch the selected data
    def get_selected_history(self, id) -> dict:
        select_query = "SELECT * FROM history WHERE id = ?"
        try:
            self.cursor.execute(select_query, (id,))
            item = self.cursor.fetchone()
            self.logger.debug(f"Selected data at get_selected_history: {item}")
            return {
                "id": item[0],
                "query": item[1],
                "response": item[2],
                "datetime": item[3],
                "model": item[4]
            }
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching data: {e}")
            return


    # function to delete the selected data
    def delete_history(self, id):
        delete_query = "DELETE FROM history WHERE id = ?"
        try:
            self.cursor.execute(delete_query, (id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting data: {e}")

    # function to delete all data inside the table
    def delete_all_history(self):
        delete_query = "DELETE FROM history"
        try:
            self.cursor.execute(delete_query)
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting data: {e}")

    def close(self):
        if self.conn:
            self.conn.close()