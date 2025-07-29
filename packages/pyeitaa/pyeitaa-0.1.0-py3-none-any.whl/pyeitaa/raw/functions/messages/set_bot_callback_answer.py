from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class SetBotCallbackAnswer(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2a70ecf6``

    Parameters:
        query_id: ``int`` ``64-bit``
        cache_time: ``int`` ``32-bit``
        alert (optional): ``bool``
        message (optional): ``str``
        url (optional): ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["query_id", "cache_time", "alert", "message", "url"]

    ID = -0x2a70ecf6
    QUALNAME = "functions.messages.SetBotCallbackAnswer"

    def __init__(self, *, query_id: int, cache_time: int, alert: Optional[bool] = None, message: Optional[str] = None, url: Optional[str] = None) -> None:
        self.query_id = query_id  # long
        self.cache_time = cache_time  # int
        self.alert = alert  # flags.1?true
        self.message = message  # flags.0?string
        self.url = url  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        alert = True if flags & (1 << 1) else False
        query_id = Long.read(data)
        
        message = String.read(data) if flags & (1 << 0) else None
        url = String.read(data) if flags & (1 << 2) else None
        cache_time = Int.read(data)
        
        return SetBotCallbackAnswer(query_id=query_id, cache_time=cache_time, alert=alert, message=message, url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.alert else 0
        flags |= (1 << 0) if self.message is not None else 0
        flags |= (1 << 2) if self.url is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        if self.message is not None:
            data.write(String(self.message))
        
        if self.url is not None:
            data.write(String(self.url))
        
        data.write(Int(self.cache_time))
        
        return data.getvalue()
