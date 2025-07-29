from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputGroupCallStream(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``0x598a92a``

    Parameters:
        call: :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        time_ms: ``int`` ``64-bit``
        scale: ``int`` ``32-bit``
        video_channel (optional): ``int`` ``32-bit``
        video_quality (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["call", "time_ms", "scale", "video_channel", "video_quality"]

    ID = 0x598a92a
    QUALNAME = "types.InputGroupCallStream"

    def __init__(self, *, call: "raw.base.InputGroupCall", time_ms: int, scale: int, video_channel: Optional[int] = None, video_quality: Optional[int] = None) -> None:
        self.call = call  # InputGroupCall
        self.time_ms = time_ms  # long
        self.scale = scale  # int
        self.video_channel = video_channel  # flags.0?int
        self.video_quality = video_quality  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        call = TLObject.read(data)
        
        time_ms = Long.read(data)
        
        scale = Int.read(data)
        
        video_channel = Int.read(data) if flags & (1 << 0) else None
        video_quality = Int.read(data) if flags & (1 << 0) else None
        return InputGroupCallStream(call=call, time_ms=time_ms, scale=scale, video_channel=video_channel, video_quality=video_quality)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.video_channel is not None else 0
        flags |= (1 << 0) if self.video_quality is not None else 0
        data.write(Int(flags))
        
        data.write(self.call.write())
        
        data.write(Long(self.time_ms))
        
        data.write(Int(self.scale))
        
        if self.video_channel is not None:
            data.write(Int(self.video_channel))
        
        if self.video_quality is not None:
            data.write(Int(self.video_quality))
        
        return data.getvalue()
