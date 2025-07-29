from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class BotCallbackAnswer(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.BotCallbackAnswer`.

    Details:
        - Layer: ``135``
        - ID: ``0x36585ea4``

    Parameters:
        cache_time: ``int`` ``32-bit``
        alert (optional): ``bool``
        has_url (optional): ``bool``
        native_ui (optional): ``bool``
        message (optional): ``str``
        url (optional): ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetBotCallbackAnswer <pyeitaa.raw.functions.messages.GetBotCallbackAnswer>`
    """

    __slots__: List[str] = ["cache_time", "alert", "has_url", "native_ui", "message", "url"]

    ID = 0x36585ea4
    QUALNAME = "types.messages.BotCallbackAnswer"

    def __init__(self, *, cache_time: int, alert: Optional[bool] = None, has_url: Optional[bool] = None, native_ui: Optional[bool] = None, message: Optional[str] = None, url: Optional[str] = None) -> None:
        self.cache_time = cache_time  # int
        self.alert = alert  # flags.1?true
        self.has_url = has_url  # flags.3?true
        self.native_ui = native_ui  # flags.4?true
        self.message = message  # flags.0?string
        self.url = url  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        alert = True if flags & (1 << 1) else False
        has_url = True if flags & (1 << 3) else False
        native_ui = True if flags & (1 << 4) else False
        message = String.read(data) if flags & (1 << 0) else None
        url = String.read(data) if flags & (1 << 2) else None
        cache_time = Int.read(data)
        
        return BotCallbackAnswer(cache_time=cache_time, alert=alert, has_url=has_url, native_ui=native_ui, message=message, url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.alert else 0
        flags |= (1 << 3) if self.has_url else 0
        flags |= (1 << 4) if self.native_ui else 0
        flags |= (1 << 0) if self.message is not None else 0
        flags |= (1 << 2) if self.url is not None else 0
        data.write(Int(flags))
        
        if self.message is not None:
            data.write(String(self.message))
        
        if self.url is not None:
            data.write(String(self.url))
        
        data.write(Int(self.cache_time))
        
        return data.getvalue()
