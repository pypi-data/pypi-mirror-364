from io import BytesIO
from typing import cast, Union, Any

from .int import Int
from ..list import List
from ..tl_object import TLObject


class Vector(bytes, TLObject):
    ID = 0x1cb5c415

    # Method added to handle the special case when a query returns a bare Vector (of Ints);
    # i.e., RpcResult body starts with 0x1cb5c415 (Vector Id) - e.g., messages.GetMessagesViews.
    @staticmethod
    def _read(b: BytesIO) -> Union[int, Any]:
        try:
            return TLObject.read(b)
        except ValueError:
            b.seek(-4, 1)
            return Int.read(b)

    @classmethod
    def read(cls, data: BytesIO, t: Any = None, *args: Any) -> List:
        return List(
            t.read(data) if t
            else Vector._read(data)
            for _ in range(Int.read(data))
        )

    def __new__(cls, value: list, t: Any = None) -> bytes:
        return b"".join(
            [Int(cls.ID, False), Int(len(value))]
            + [cast(bytes, t(i)) if t else i.write() for i in value]
        )
