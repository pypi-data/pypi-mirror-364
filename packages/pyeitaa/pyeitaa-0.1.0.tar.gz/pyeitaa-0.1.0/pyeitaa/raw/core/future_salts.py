from io import BytesIO
from typing import Any, List

from .future_salt import FutureSalt
from .primitives.int import Int, Long
from .tl_object import TLObject


class FutureSalts(TLObject):
    ID = -0x51aff76b

    __slots__ = ["req_msg_id", "now", "salts"]

    QUALNAME = "FutureSalts"

    def __init__(self, req_msg_id: int, now: int, salts: List[FutureSalt]):
        self.req_msg_id = req_msg_id
        self.now = now
        self.salts = salts

    @staticmethod
    def read(data: BytesIO, *args: Any) -> "FutureSalts":
        req_msg_id = Long.read(data)
        now = Int.read(data)

        count = Int.read(data)
        salts = [FutureSalt.read(data) for _ in range(count)]

        return FutureSalts(req_msg_id, now, salts)
