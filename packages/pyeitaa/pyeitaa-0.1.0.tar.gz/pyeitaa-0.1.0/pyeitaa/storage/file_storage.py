import logging
import os
import sqlite3
from pathlib import Path

from .sqlite_storage import SQLiteStorage

log = logging.getLogger(__name__)


class FileStorage(SQLiteStorage):
    FILE_EXTENSION = ".session"

    def __init__(self, name: str, workdir: Path):
        super().__init__(name)

        self.database = workdir / (self.name + self.FILE_EXTENSION)

    async def open(self):
        file_exists = self.database.is_file()

        self.conn = sqlite3.connect(str(self.database), timeout=1, check_same_thread=False)

        if not file_exists:
            self.create()

        with self.conn:
            self.conn.execute("VACUUM")

    async def delete(self):
        os.remove(self.database)
