import sqlite3
from pathlib import Path
from PySide6.QtCore import QObject
import re
from models.llm_client_worker import LLMResults
from typing import List

class DatabaseManager(QObject):
    def __init__(self, logger, db_path):
        super().__init__()
        self.logger = logger
        self.db_name = Path(db_path)
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

        # if some columns are missing, add them
        self.cursor.execute("PRAGMA table_info(history)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if "temperature" not in columns:
            self.cursor.execute("ALTER TABLE history ADD COLUMN temperature INTEGER")
            self.conn



    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        # Handle the exception if the self_db_name is not found)

        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {e}")

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            datetime TEXT NOT NULL,
            model TEXT NOT NULL,
            temperature INTEGER
        )
        """
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error creating table: {e}")

    def insert_history(self, result: LLMResults):
        insert_query = """
        INSERT INTO history (query, response, datetime, model, temperature)
        VALUES (?, ?, ?, ?, ?)
        """

        try:
            self.cursor.execute(
                insert_query,
                (result.prompt, result.response, result.datetime, result.model, result.temperature),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting data: {e}")

    def get_n_history(self, n) -> List[LLMResults]:
        select_query = "SELECT * FROM history ORDER BY datetime DESC LIMIT ?"
        try:
            self.cursor.execute(select_query, (n,))
            items = []
            for item in self.cursor.fetchall():

                items.append(
                    LLMResults(
                        id=item[0],
                        prompt=item[1],
                        response=item[2],
                        datetime=item[3],
                        model=item[4],
                        temperature=item[5]
                    )
                )
            return items

        except sqlite3.Error as e:
            self.logger.error(f"Error fetching data: {e}")
            return []

    def get_one_item(self, id) -> LLMResults:
        select_query = "SELECT * FROM history WHERE id = ?"
        try:
            self.cursor.execute(select_query, (id,))
            item = self.cursor.fetchone()
            if item:
                return LLMResults(
                    id=item[0],
                    prompt=item[1],
                    response=item[2],
                    datetime=item[3],
                    model=item[4],
                    temperature=item[5]
                )
            else:
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching data: {e}")
            return None

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

    def search(self, word:str) -> List[LLMResults]:
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
                - temperature (int): The temperature associated with the item.
        """
        # separate the words by space or full-width space
        words = re.split(r"[\s　]+", word)

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
                items.append(
                    LLMResults(
                        id=item[0],
                        prompt=item[1],
                        response=item[2],
                        datetime=item[3],
                        model=item[4],
                        temperature=item[5],
                    )
                )
            return items
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching data: {e}")
            return []

    def get_latest_item(self) -> LLMResults:
        """
        Get the latest record in the history table.

        Returns:
        dict: A dictionary representing the latest item. It contains the following keys:
            - id (int): The ID of the item.
            - query (str): The query associated with the item.
            - response (str): The response associated with the item.
            - datetime (str): The datetime of the item.
            - model (str): The model associated with the item.
            - temperature (int): The temperature associated with the item.
        """
            
        select_query = "SELECT * FROM history ORDER BY id DESC LIMIT 1"
        try:
            self.cursor.execute(select_query)
            row = self.cursor.fetchone()
            if row:
                return LLMResults(
                    id=row[0],
                    prompt=row[1],
                    response=row[2],
                    datetime=row[3],
                    model=row[4],
                    temperature=row[5],
                )
            else:
                return None
        except sqlite3.Error as e:
            self.logger.error(f"Error fetching data: {e}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()
