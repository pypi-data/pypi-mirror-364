from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SetInlineBotResults(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x14a15dfa``

    Parameters:
        query_id: ``int`` ``64-bit``
        results: List of :obj:`InputBotInlineResult <pyeitaa.raw.base.InputBotInlineResult>`
        cache_time: ``int`` ``32-bit``
        gallery (optional): ``bool``
        private (optional): ``bool``
        next_offset (optional): ``str``
        switch_pm (optional): :obj:`InlineBotSwitchPM <pyeitaa.raw.base.InlineBotSwitchPM>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["query_id", "results", "cache_time", "gallery", "private", "next_offset", "switch_pm"]

    ID = -0x14a15dfa
    QUALNAME = "functions.messages.SetInlineBotResults"

    def __init__(self, *, query_id: int, results: List["raw.base.InputBotInlineResult"], cache_time: int, gallery: Optional[bool] = None, private: Optional[bool] = None, next_offset: Optional[str] = None, switch_pm: "raw.base.InlineBotSwitchPM" = None) -> None:
        self.query_id = query_id  # long
        self.results = results  # Vector<InputBotInlineResult>
        self.cache_time = cache_time  # int
        self.gallery = gallery  # flags.0?true
        self.private = private  # flags.1?true
        self.next_offset = next_offset  # flags.2?string
        self.switch_pm = switch_pm  # flags.3?InlineBotSwitchPM

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        gallery = True if flags & (1 << 0) else False
        private = True if flags & (1 << 1) else False
        query_id = Long.read(data)
        
        results = TLObject.read(data)
        
        cache_time = Int.read(data)
        
        next_offset = String.read(data) if flags & (1 << 2) else None
        switch_pm = TLObject.read(data) if flags & (1 << 3) else None
        
        return SetInlineBotResults(query_id=query_id, results=results, cache_time=cache_time, gallery=gallery, private=private, next_offset=next_offset, switch_pm=switch_pm)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.gallery else 0
        flags |= (1 << 1) if self.private else 0
        flags |= (1 << 2) if self.next_offset is not None else 0
        flags |= (1 << 3) if self.switch_pm is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        data.write(Vector(self.results))
        
        data.write(Int(self.cache_time))
        
        if self.next_offset is not None:
            data.write(String(self.next_offset))
        
        if self.switch_pm is not None:
            data.write(self.switch_pm.write())
        
        return data.getvalue()
