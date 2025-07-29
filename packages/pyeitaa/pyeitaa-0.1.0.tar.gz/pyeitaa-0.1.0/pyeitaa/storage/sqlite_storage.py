import time
from threading import Lock
from typing import Any, Optional

from .storage import Storage
from ..raw.base.input_peer import InputPeer
from ..raw.types import InputPeerUser, InputPeerChat, InputPeerChannel

# language=SQLite
SCHEMA = """
CREATE TABLE sessions
(
    token     TEXT,
    imei      TEXT,
    date      INTEGER,
    user_id   INTEGER
);

CREATE TABLE peers
(
    id             INTEGER PRIMARY KEY,
    access_hash    INTEGER,
    type           TEXT NOT NULL,
    username       TEXT,
    phone_number   TEXT,
    last_update_on INTEGER NOT NULL DEFAULT (CAST(STRFTIME('%s', 'now') AS INTEGER))
);

CREATE INDEX idx_peers_id ON peers (id);
CREATE INDEX idx_peers_username ON peers (username);
CREATE INDEX idx_peers_phone_number ON peers (phone_number);

CREATE TRIGGER trg_peers_last_update_on
    AFTER UPDATE
    ON peers
BEGIN
    UPDATE peers
    SET last_update_on = CAST(STRFTIME('%s', 'now') AS INTEGER)
    WHERE id = NEW.id;
END;
"""

class Query:
    get_peer_by_id = "SELECT id, access_hash, type FROM peers WHERE id = ?"
    get_peer_by_username = "SELECT id, access_hash, type FROM peers WHERE username = ?"
    get_peer_by_phone_number = "SELECT id, access_hash, type FROM peers WHERE phone_number = ?"

    get_session_full = "SELECT token, imei, user_id from sessions"
    get_session_attribute = "SELECT {} FROM sessions"
    set_session_attribute = "UPDATE sessions SET {} = ?"

    update_peers = "REPLACE INTO peers (id, access_hash, type, username, phone_number) VALUES (?, ?, ?, ?, ?)"
    create_session = "INSERT INTO sessions VALUES (?, ?, ?, ?)"

def get_input_peer(peer_id: int, access_hash: int, peer_type: str) -> InputPeer:
    match peer_type:
        case "user" | "bot":
            return InputPeerUser(
                user_id=peer_id,
                access_hash=access_hash
            )

        case "group":
            return InputPeerChat(
                chat_id=peer_id
            )

        case "channel" | "supergroup" | "megagroup":
            return InputPeerChannel(
                channel_id=peer_id,
                access_hash=access_hash
            )

    raise ValueError(f"Invalid peer type: {peer_type}")


class SQLiteStorage(Storage):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.conn = None  # type: sqlite3.Connection
        self.lock = Lock()

        self._token = None
        self._imei = None
        self._date = None
        self._user_id = None

    def create(self) -> None:
        with self.lock, self.conn:
            self.conn.executescript(SCHEMA)

            self.conn.execute(
                Query.create_session, (None, None, None, None)
            )

            self.conn.commit()

    def save(self) -> None:
        self.date = int(time.time())

        with self.lock:
            self.conn.commit()

    def close(self) -> None:
        with self.lock:
            self.conn.close()

    def update_peers(self, peers: list[tuple[int, Optional[int], str, Optional[str], Optional[str]]]) -> None:
        with self.lock:
            self.conn.executemany(Query.update_peers, peers)
            self.conn.commit()

    def get_peer(self, attribute: Any, query: str) -> InputPeer:
        with self.lock:
            r = self.conn.execute(query, (attribute,)).fetchone()

        if r is None:
            return

        return get_input_peer(*r)

    def get_session_attribute(self, attribute: str) -> str | int:
        with self.lock:
            return self.conn.execute(Query.get_session_attribute.format(attribute)).fetchone()[0]

    def set_session_attribute(self, attribute: str, value: str | int) -> None:
        with self.lock:
            self.conn.execute(Query.set_session_attribute.format(attribute), (value,))
            self.conn.commit()

    def get_full_session(self) -> tuple[str, str, int]:
        with self.lock:
            return self.conn.execute(Query.get_session_full).fetchone()

    def get_peer_by_id(self, peer_id: int) -> InputPeer:
        return self.get_peer(peer_id, Query.get_peer_by_id)

    def get_peer_by_username(self, username: str) -> InputPeer:
        return self.get_peer(username, Query.get_peer_by_username)

    def get_peer_by_phone_number(self, phone_number: str) -> InputPeer:
        return self.get_peer(phone_number, Query.get_peer_by_phone_number)

    @property
    def token(self) -> str:
        return self._token or self.get_session_attribute("token")

    @token.setter
    def token(self, token: str) -> None:
        self._token = token
        return self.set_session_attribute("token", token)

    @property
    def imei(self) -> str:
        return self._imei or self.get_session_attribute("imei")

    @imei.setter
    def imei(self, imei: str) -> None:
        self._imei = imei
        return self.set_session_attribute("imei", imei)

    @property
    def date(self) -> int:
        return self._date or self.get_session_attribute("date")

    @date.setter
    def date(self, date: str) -> None:
        self._date = date
        return self.set_session_attribute("date", date)

    @property
    def user_id(self) -> int:
        return self._user_id or self.get_session_attribute("user_id")

    @user_id.setter
    def user_id(self, user_id: str) -> None:
        self._user_id = user_id
        return self.set_session_attribute("user_id", user_id)
