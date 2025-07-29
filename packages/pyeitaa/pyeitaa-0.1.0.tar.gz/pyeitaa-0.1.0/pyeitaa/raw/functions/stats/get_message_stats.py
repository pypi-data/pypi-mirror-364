from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetMessageStats(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x491f5c0b``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        msg_id: ``int`` ``32-bit``
        dark (optional): ``bool``

    Returns:
        :obj:`stats.MessageStats <pyeitaa.raw.base.stats.MessageStats>`
    """

    __slots__: List[str] = ["channel", "msg_id", "dark"]

    ID = -0x491f5c0b
    QUALNAME = "functions.stats.GetMessageStats"

    def __init__(self, *, channel: "raw.base.InputChannel", msg_id: int, dark: Optional[bool] = None) -> None:
        self.channel = channel  # InputChannel
        self.msg_id = msg_id  # int
        self.dark = dark  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        dark = True if flags & (1 << 0) else False
        channel = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        return GetMessageStats(channel=channel, msg_id=msg_id, dark=dark)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.dark else 0
        data.write(Int(flags))
        
        data.write(self.channel.write())
        
        data.write(Int(self.msg_id))
        
        return data.getvalue()
