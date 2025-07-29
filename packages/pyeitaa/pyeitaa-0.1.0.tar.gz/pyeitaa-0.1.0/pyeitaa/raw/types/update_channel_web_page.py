from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateChannelWebPage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x2f2ba99f``

    Parameters:
        channel_id: ``int`` ``64-bit``
        webpage: :obj:`WebPage <pyeitaa.raw.base.WebPage>`
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "webpage", "pts", "pts_count"]

    ID = 0x2f2ba99f
    QUALNAME = "types.UpdateChannelWebPage"

    def __init__(self, *, channel_id: int, webpage: "raw.base.WebPage", pts: int, pts_count: int) -> None:
        self.channel_id = channel_id  # long
        self.webpage = webpage  # WebPage
        self.pts = pts  # int
        self.pts_count = pts_count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        webpage = TLObject.read(data)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        return UpdateChannelWebPage(channel_id=channel_id, webpage=webpage, pts=pts, pts_count=pts_count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(self.webpage.write())
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        return data.getvalue()
