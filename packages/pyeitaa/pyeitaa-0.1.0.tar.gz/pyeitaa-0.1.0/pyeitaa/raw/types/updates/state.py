from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class State(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.updates.State`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5a93d5c2``

    Parameters:
        pts: ``int`` ``32-bit``
        qts: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
        seq: ``int`` ``32-bit``
        unread_count: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetState <pyeitaa.raw.functions.updates.GetState>`
    """

    __slots__: List[str] = ["pts", "qts", "date", "seq", "unread_count"]

    ID = -0x5a93d5c2
    QUALNAME = "types.updates.State"

    def __init__(self, *, pts: int, qts: int, date: int, seq: int, unread_count: int) -> None:
        self.pts = pts  # int
        self.qts = qts  # int
        self.date = date  # int
        self.seq = seq  # int
        self.unread_count = unread_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pts = Int.read(data)
        
        qts = Int.read(data)
        
        date = Int.read(data)
        
        seq = Int.read(data)
        
        unread_count = Int.read(data)
        
        return State(pts=pts, qts=qts, date=date, seq=seq, unread_count=unread_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.pts))
        
        data.write(Int(self.qts))
        
        data.write(Int(self.date))
        
        data.write(Int(self.seq))
        
        data.write(Int(self.unread_count))
        
        return data.getvalue()
