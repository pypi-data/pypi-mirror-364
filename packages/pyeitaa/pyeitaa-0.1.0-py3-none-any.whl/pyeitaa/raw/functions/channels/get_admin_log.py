from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetAdminLog(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x33ddf480``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        q: ``str``
        max_id: ``int`` ``64-bit``
        min_id: ``int`` ``64-bit``
        limit: ``int`` ``32-bit``
        events_filter (optional): :obj:`ChannelAdminLogEventsFilter <pyeitaa.raw.base.ChannelAdminLogEventsFilter>`
        admins (optional): List of :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`channels.AdminLogResults <pyeitaa.raw.base.channels.AdminLogResults>`
    """

    __slots__: List[str] = ["channel", "q", "max_id", "min_id", "limit", "events_filter", "admins"]

    ID = 0x33ddf480
    QUALNAME = "functions.channels.GetAdminLog"

    def __init__(self, *, channel: "raw.base.InputChannel", q: str, max_id: int, min_id: int, limit: int, events_filter: "raw.base.ChannelAdminLogEventsFilter" = None, admins: Optional[List["raw.base.InputUser"]] = None) -> None:
        self.channel = channel  # InputChannel
        self.q = q  # string
        self.max_id = max_id  # long
        self.min_id = min_id  # long
        self.limit = limit  # int
        self.events_filter = events_filter  # flags.0?ChannelAdminLogEventsFilter
        self.admins = admins  # flags.1?Vector<InputUser>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        channel = TLObject.read(data)
        
        q = String.read(data)
        
        events_filter = TLObject.read(data) if flags & (1 << 0) else None
        
        admins = TLObject.read(data) if flags & (1 << 1) else []
        
        max_id = Long.read(data)
        
        min_id = Long.read(data)
        
        limit = Int.read(data)
        
        return GetAdminLog(channel=channel, q=q, max_id=max_id, min_id=min_id, limit=limit, events_filter=events_filter, admins=admins)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.events_filter is not None else 0
        flags |= (1 << 1) if self.admins is not None else 0
        data.write(Int(flags))
        
        data.write(self.channel.write())
        
        data.write(String(self.q))
        
        if self.events_filter is not None:
            data.write(self.events_filter.write())
        
        if self.admins is not None:
            data.write(Vector(self.admins))
        
        data.write(Long(self.max_id))
        
        data.write(Long(self.min_id))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
