from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateWebPage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x7f891213``

    Parameters:
        webpage: :obj:`WebPage <pyeitaa.raw.base.WebPage>`
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["webpage", "pts", "pts_count"]

    ID = 0x7f891213
    QUALNAME = "types.UpdateWebPage"

    def __init__(self, *, webpage: "raw.base.WebPage", pts: int, pts_count: int) -> None:
        self.webpage = webpage  # WebPage
        self.pts = pts  # int
        self.pts_count = pts_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        webpage = TLObject.read(data)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdateWebPage(webpage=webpage, pts=pts, pts_count=pts_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.webpage.write())
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()
