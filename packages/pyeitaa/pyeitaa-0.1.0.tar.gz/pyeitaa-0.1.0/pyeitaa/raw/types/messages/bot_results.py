from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class BotResults(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.BotResults`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6b8357b8``

    Parameters:
        query_id: ``int`` ``64-bit``
        results: List of :obj:`BotInlineResult <pyeitaa.raw.base.BotInlineResult>`
        cache_time: ``int`` ``32-bit``
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        gallery (optional): ``bool``
        next_offset (optional): ``str``
        switch_pm (optional): :obj:`InlineBotSwitchPM <pyeitaa.raw.base.InlineBotSwitchPM>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetInlineBotResults <pyeitaa.raw.functions.messages.GetInlineBotResults>`
    """

    __slots__: List[str] = ["query_id", "results", "cache_time", "users", "gallery", "next_offset", "switch_pm"]

    ID = -0x6b8357b8
    QUALNAME = "types.messages.BotResults"

    def __init__(self, *, query_id: int, results: List["raw.base.BotInlineResult"], cache_time: int, users: List["raw.base.User"], gallery: Optional[bool] = None, next_offset: Optional[str] = None, switch_pm: "raw.base.InlineBotSwitchPM" = None) -> None:
        self.query_id = query_id  # long
        self.results = results  # Vector<BotInlineResult>
        self.cache_time = cache_time  # int
        self.users = users  # Vector<User>
        self.gallery = gallery  # flags.0?true
        self.next_offset = next_offset  # flags.1?string
        self.switch_pm = switch_pm  # flags.2?InlineBotSwitchPM

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        gallery = True if flags & (1 << 0) else False
        query_id = Long.read(data)
        
        next_offset = String.read(data) if flags & (1 << 1) else None
        switch_pm = TLObject.read(data) if flags & (1 << 2) else None
        
        results = TLObject.read(data)
        
        cache_time = Int.read(data)
        
        users = TLObject.read(data)
        
        return BotResults(query_id=query_id, results=results, cache_time=cache_time, users=users, gallery=gallery, next_offset=next_offset, switch_pm=switch_pm)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.gallery else 0
        flags |= (1 << 1) if self.next_offset is not None else 0
        flags |= (1 << 2) if self.switch_pm is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        if self.next_offset is not None:
            data.write(String(self.next_offset))
        
        if self.switch_pm is not None:
            data.write(self.switch_pm.write())
        
        data.write(Vector(self.results))
        
        data.write(Int(self.cache_time))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
