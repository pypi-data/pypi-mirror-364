from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class DocumentAttributeVideo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DocumentAttribute`.

    Details:
        - Layer: ``135``
        - ID: ``0xef02ce6``

    Parameters:
        duration: ``int`` ``32-bit``
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
        round_message (optional): ``bool``
        supports_streaming (optional): ``bool``
    """

    __slots__: List[str] = ["duration", "w", "h", "round_message", "supports_streaming"]

    ID = 0xef02ce6
    QUALNAME = "types.DocumentAttributeVideo"

    def __init__(self, *, duration: int, w: int, h: int, round_message: Optional[bool] = None, supports_streaming: Optional[bool] = None) -> None:
        self.duration = duration  # int
        self.w = w  # int
        self.h = h  # int
        self.round_message = round_message  # flags.0?true
        self.supports_streaming = supports_streaming  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        round_message = True if flags & (1 << 0) else False
        supports_streaming = True if flags & (1 << 1) else False
        duration = Int.read(data)
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        return DocumentAttributeVideo(duration=duration, w=w, h=h, round_message=round_message, supports_streaming=supports_streaming)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.round_message else 0
        flags |= (1 << 1) if self.supports_streaming else 0
        data.write(Int(flags))
        
        data.write(Int(self.duration))
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        return data.getvalue()
