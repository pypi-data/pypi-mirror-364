from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetChannelDifference(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3173d78``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        filter: :obj:`ChannelMessagesFilter <pyeitaa.raw.base.ChannelMessagesFilter>`
        pts: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        force (optional): ``bool``

    Returns:
        :obj:`updates.ChannelDifference <pyeitaa.raw.base.updates.ChannelDifference>`
    """

    __slots__: List[str] = ["channel", "filter", "pts", "limit", "force"]

    ID = 0x3173d78
    QUALNAME = "functions.updates.GetChannelDifference"

    def __init__(self, *, channel: "raw.base.InputChannel", filter: "raw.base.ChannelMessagesFilter", pts: int, limit: int, force: Optional[bool] = None) -> None:
        self.channel = channel  # InputChannel
        self.filter = filter  # ChannelMessagesFilter
        self.pts = pts  # int
        self.limit = limit  # int
        self.force = force  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        force = True if flags & (1 << 0) else False
        channel = TLObject.read(data)
        
        filter = TLObject.read(data)
        
        pts = Int.read(data)
        
        limit = Int.read(data)
        
        return GetChannelDifference(channel=channel, filter=filter, pts=pts, limit=limit, force=force)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.force else 0
        data.write(Int(flags))
        
        data.write(self.channel.write())
        
        data.write(self.filter.write())
        
        data.write(Int(self.pts))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
