from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Double
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class VideoSize(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.VideoSize`.

    Details:
        - Layer: ``135``
        - ID: ``-0x21cc4f6c``

    Parameters:
        type: ``str``
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
        size: ``int`` ``32-bit``
        video_start_ts (optional): ``float`` ``64-bit``
    """

    __slots__: List[str] = ["type", "w", "h", "size", "video_start_ts"]

    ID = -0x21cc4f6c
    QUALNAME = "types.VideoSize"

    def __init__(self, *, type: str, w: int, h: int, size: int, video_start_ts: Optional[float] = None) -> None:
        self.type = type  # string
        self.w = w  # int
        self.h = h  # int
        self.size = size  # int
        self.video_start_ts = video_start_ts  # flags.0?double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        type = String.read(data)
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        size = Int.read(data)
        
        video_start_ts = Double.read(data) if flags & (1 << 0) else None
        return VideoSize(type=type, w=w, h=h, size=size, video_start_ts=video_start_ts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.video_start_ts is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.type))
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        data.write(Int(self.size))
        
        if self.video_start_ts is not None:
            data.write(Double(self.video_start_ts))
        
        return data.getvalue()
