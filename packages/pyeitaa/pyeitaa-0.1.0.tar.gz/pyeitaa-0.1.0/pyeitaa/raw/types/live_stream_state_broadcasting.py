from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class LiveStreamStateBroadcasting(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LiveStreamState`.

    Details:
        - Layer: ``135``
        - ID: ``-0x44a4a20b``

    Parameters:
        liveStream: :obj:`LiveStream <pyeitaa.raw.base.LiveStream>`
        paused (optional): ``bool``
    """

    __slots__: List[str] = ["liveStream", "paused"]

    ID = -0x44a4a20b
    QUALNAME = "types.LiveStreamStateBroadcasting"

    def __init__(self, *, liveStream: "raw.base.LiveStream", paused: Optional[bool] = None) -> None:
        self.liveStream = liveStream  # LiveStream
        self.paused = paused  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        paused = True if flags & (1 << 0) else False
        liveStream = TLObject.read(data)
        
        return LiveStreamStateBroadcasting(liveStream=liveStream, paused=paused)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.paused else 0
        data.write(Int(flags))
        
        data.write(self.liveStream.write())
        
        return data.getvalue()
