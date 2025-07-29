from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AffectedHistory(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.AffectedHistory`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4ba3962f``

    Parameters:
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
        offset: ``int`` ``32-bit``

    See Also:
        This object can be returned by 4 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.DeleteHistory <pyeitaa.raw.functions.messages.DeleteHistory>`
            - :obj:`messages.ReadMentions <pyeitaa.raw.functions.messages.ReadMentions>`
            - :obj:`messages.UnpinAllMessages <pyeitaa.raw.functions.messages.UnpinAllMessages>`
            - :obj:`channels.DeleteUserHistory <pyeitaa.raw.functions.channels.DeleteUserHistory>`
    """

    __slots__: List[str] = ["pts", "pts_count", "offset"]

    ID = -0x4ba3962f
    QUALNAME = "types.messages.AffectedHistory"

    def __init__(self, *, pts: int, pts_count: int, offset: int) -> None:
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.offset = offset  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        offset = Int.read(data)
        
        return AffectedHistory(pts=pts, pts_count=pts_count, offset=offset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        data.write(Int(self.offset))
        
        return data.getvalue()
