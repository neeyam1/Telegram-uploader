import sqlite3
import os

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initialize the database and create the table if it doesn't exist."""
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploaded_media (
                id TEXT PRIMARY KEY,
                filename TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def is_uploaded(self, media_id):
        """Check if a media item has already been uploaded."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM uploaded_media WHERE id = ?', (media_id,))
        return cursor.fetchone() is not None

    def add_uploaded(self, media_id, filename):
        """Mark a media item as uploaded."""
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO uploaded_media (id, filename) VALUES (?, ?)', (media_id, filename))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Already exists, which is fine
            pass

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
