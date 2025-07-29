import logging
from time import time
from datetime import datetime, UTC

log = logging.getLogger(__name__)


class MsgId:
    reference_clock = 0
    last_time = 0
    msg_id_offset = 0
    server_time = 0

    def __new__(cls) -> int:
        now = time() - cls.reference_clock + cls.server_time
        cls.msg_id_offset = cls.msg_id_offset + 4 if now == cls.last_time else 0
        msg_id = int(now * 2 ** 32) + cls.msg_id_offset
        cls.last_time = now

        return msg_id

    @classmethod
    def set_server_time(cls, server_time: int):
        if not cls.server_time:
            cls.reference_clock = time()
            cls.server_time = server_time

            log.info(f"Time synced: {datetime.fromtimestamp(server_time, tz=UTC)} UTC")