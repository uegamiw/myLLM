import sqlite3
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject
import re

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

    def get_n_history(self, n) -> list:
        """
        Retrieves the latest 'n' history items from the database.

        Args:
            n (int): The number of history items to retrieve.

        Returns:
            list: A list of dictionaries representing the retrieved history items. Each dictionary contains the following keys:
                - 'id' (int): The ID of the history item.
                - 'query' (str): The query associated with the history item.
                - 'response' (str): The response associated with the history item.
                - 'datetime' (str): The datetime of the history item.
                - 'model' (str): The model associated with the history item.

            If an error occurs while fetching the data, an empty list is returned.
        """
        select_query = "SELECT * FROM history ORDER BY datetime DESC LIMIT ?"
        try:
            self.cursor.execute(select_query, (n,))
            items = []
            for item in self.cursor.fetchall():

                items.append({
                    "id": item[0],
                    "query": item[1],
                    "response": item[2],
                    "datetime": item[3],
                    "model": item[4]
                })
            return items

        except sqlite3.Error as e:
            self.logger.error(f"Error fetching data: {e}")
            return []


    def delete_history(self, id):
        """
        Delete a record from the 'history' table based on the given id.

        Parameters:
        - id: The id of the record to be deleted.

        Raises:
        - sqlite3.Error: If there is an error deleting the data.

        Returns:
        None
        """
        delete_query = "DELETE FROM history WHERE id = ?"
        try:
            self.cursor.execute(delete_query, (id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting data: {e}")


    def search(self, word):
        """
        Search for items in the history table based on a given word.
        Args:
            word (str): The word to search for.
        Returns:
            list: A list of dictionaries representing the matching items. Each dictionary contains the following keys:
                - id (int): The ID of the item.
                - query (str): The query associated with the item.
                - response (str): The response associated with the item.
                - datetime (str): The datetime of the item.
                - model (str): The model associated with the item.
        """
        # separate the words by space or full-width space
        words = re.split(r'[\s　]+', word)
        
        # develop the search query
        conditions = []
        params = []
        for w in words:
            conditions.append("(query LIKE ? OR response LIKE ?)")
            params.extend([f"%{w}%", f"%{w}%"])
        
        search_query = f"SELECT * FROM history WHERE {' AND '.join(conditions)} ORDER BY datetime DESC LIMIT 100"
        
        try:
            self.cursor.execute(search_query, params)
            items = []
            for item in self.cursor.fetchall():
                items.append({
                    "id": item[0],
                    "query": item[1],
                    "response": item[2],
                    "datetime": item[3],
                    "model": item[4]
                })
            return items
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching data: {e}")
            return []
    

    def close(self):
        if self.conn:
            self.conn.close()