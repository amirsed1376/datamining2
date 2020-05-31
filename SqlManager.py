import sqlite3


class SqlManager:
    def __init__(self, file):
        self.conn = sqlite3.connect(file)
        self.crs = self.conn.cursor()
