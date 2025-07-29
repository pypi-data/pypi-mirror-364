from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ExportMessageLink(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x19c05215``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        id: ``int`` ``32-bit``
        grouped (optional): ``bool``
        thread (optional): ``bool``

    Returns:
        :obj:`ExportedMessageLink <pyeitaa.raw.base.ExportedMessageLink>`
    """

    __slots__: List[str] = ["channel", "id", "grouped", "thread"]

    ID = -0x19c05215
    QUALNAME = "functions.channels.ExportMessageLink"

    def __init__(self, *, channel: "raw.base.InputChannel", id: int, grouped: Optional[bool] = None, thread: Optional[bool] = None) -> None:
        self.channel = channel  # InputChannel
        self.id = id  # int
        self.grouped = grouped  # flags.0?true
        self.thread = thread  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        grouped = True if flags & (1 << 0) else False
        thread = True if flags & (1 << 1) else False
        channel = TLObject.read(data)
        
        id = Int.read(data)
        
        return ExportMessageLink(channel=channel, id=id, grouped=grouped, thread=thread)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.grouped else 0
        flags |= (1 << 1) if self.thread else 0
        data.write(Int(flags))
        
        data.write(self.channel.write())
        
        data.write(Int(self.id))
        
        return data.getvalue()
