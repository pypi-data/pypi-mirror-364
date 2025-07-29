import sqlite3 as db
import os

_dir = os.path.dirname(__file__)
db_path = os.path.join(_dir, '.sqlite')

class _Database:
    def __init__(self):
        # os.remove(db_path) # debug
        self.conn = db.connect(db_path, check_same_thread=False) # creates file
    def __del__(self):
        self.conn.close()
    def _delete(self):
        self.conn.close()
        os.remove(db_path)
        

