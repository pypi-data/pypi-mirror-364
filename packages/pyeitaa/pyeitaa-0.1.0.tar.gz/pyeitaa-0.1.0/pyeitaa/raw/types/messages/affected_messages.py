from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AffectedMessages(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.AffectedMessages`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7b2e6e7b``

    Parameters:
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``

    See Also:
        This object can be returned by 4 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.ReadHistory <pyeitaa.raw.functions.messages.ReadHistory>`
            - :obj:`messages.DeleteMessages <pyeitaa.raw.functions.messages.DeleteMessages>`
            - :obj:`messages.ReadMessageContents <pyeitaa.raw.functions.messages.ReadMessageContents>`
            - :obj:`channels.DeleteMessages <pyeitaa.raw.functions.channels.DeleteMessages>`
    """

    __slots__: List[str] = ["pts", "pts_count"]

    ID = -0x7b2e6e7b
    QUALNAME = "types.messages.AffectedMessages"

    def __init__(self, *, pts: int, pts_count: int) -> None:
        self.pts = pts  # int
        self.pts_count = pts_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return AffectedMessages(pts=pts, pts_count=pts_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()
