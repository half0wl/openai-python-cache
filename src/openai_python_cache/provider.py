import hashlib
import sqlite3
import json

from typing import TypedDict, Optional


class CacheSettings(TypedDict):
    db_loc: str


DEFAULT_CACHE_SETTINGS: CacheSettings = {
    "db_loc": "./openai_cache.db",
}


class Sqlite3CacheProvider(object):
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS cache(
        key string PRIMARY KEY NOT NULL,
        request_params json NOT NULL,
        response json NOT NULL
    );
    """

    def __init__(self, settings: CacheSettings = DEFAULT_CACHE_SETTINGS):
        self.conn: sqlite3.Connection = sqlite3.connect(settings.get("db_loc"))
        self.create_table_if_not_exists()

    def get_curr(self) -> sqlite3.Cursor:
        return self.conn.cursor()

    def create_table_if_not_exists(self):
        self.get_curr().execute(self.CREATE_TABLE)

    def hash_params(self, params: dict):
        stringified = json.dumps(params).encode("utf-8")
        hashed = hashlib.md5(stringified).hexdigest()
        return hashed

    def get(self, key: str) -> Optional[str]:
        res = (
            self.get_curr()
            .execute("SELECT * FROM cache WHERE key= ?", (key,))
            .fetchone()
        )
        return res[-1] if res else None

    def insert(self, key: str, request: dict, response: dict):
        self.get_curr().execute(
            "INSERT INTO cache VALUES (?, ?, ?)",
            (
                key,
                json.dumps(request),
                json.dumps(response),
            ),
        )
        self.conn.commit()
