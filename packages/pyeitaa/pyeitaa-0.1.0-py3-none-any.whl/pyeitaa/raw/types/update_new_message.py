from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateNewMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x1f2b0afd``

    Parameters:
        message: :obj:`Message <pyeitaa.raw.base.Message>`
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["message", "pts", "pts_count"]

    ID = 0x1f2b0afd
    QUALNAME = "types.UpdateNewMessage"

    def __init__(self, *, message: "raw.base.Message", pts: int, pts_count: int) -> None:
        self.message = message  # Message
        self.pts = pts  # int
        self.pts_count = pts_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        message = TLObject.read(data)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdateNewMessage(message=message, pts=pts, pts_count=pts_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.message.write())
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()
