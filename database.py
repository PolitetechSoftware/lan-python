import sqlite3
import logging
import threading


class AsyncDatabase:
    def __init__(self, db_name='tracker.db'):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    function_name TEXT NOT NULL,
                    calls INTEGER NOT NULL,
                    avg_execution_time REAL NOT NULL,
                    errors INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_metrics(self, func_name, metrics):
        threading.Thread(target=self._save_to_db, args=(func_name, metrics)).start()

    def _save_to_db(self, func_name, metrics):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO metrics (function_name, calls, avg_execution_time, errors)
                    VALUES (?, ?, ?, ?)
                ''', (func_name, metrics["calls"], metrics["total_time"], metrics["errors"]))
                conn.commit()
        except Exception as e:
            logging.error("Error while saving metrics to the database", exc_info=True)

    def read_metrics(self, func_name):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM metrics WHERE function_name = ?
            ''', (func_name,))
            return cursor.fetchall()
