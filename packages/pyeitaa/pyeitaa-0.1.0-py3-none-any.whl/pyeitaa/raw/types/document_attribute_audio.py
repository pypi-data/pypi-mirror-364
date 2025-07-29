from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class DocumentAttributeAudio(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DocumentAttribute`.

    Details:
        - Layer: ``135``
        - ID: ``-0x67ad063a``

    Parameters:
        duration: ``int`` ``32-bit``
        voice (optional): ``bool``
        title (optional): ``str``
        performer (optional): ``str``
        waveform (optional): ``bytes``
    """

    __slots__: List[str] = ["duration", "voice", "title", "performer", "waveform"]

    ID = -0x67ad063a
    QUALNAME = "types.DocumentAttributeAudio"

    def __init__(self, *, duration: int, voice: Optional[bool] = None, title: Optional[str] = None, performer: Optional[str] = None, waveform: Optional[bytes] = None) -> None:
        self.duration = duration  # int
        self.voice = voice  # flags.10?true
        self.title = title  # flags.0?string
        self.performer = performer  # flags.1?string
        self.waveform = waveform  # flags.2?bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        voice = True if flags & (1 << 10) else False
        duration = Int.read(data)
        
        title = String.read(data) if flags & (1 << 0) else None
        performer = String.read(data) if flags & (1 << 1) else None
        waveform = Bytes.read(data) if flags & (1 << 2) else None
        return DocumentAttributeAudio(duration=duration, voice=voice, title=title, performer=performer, waveform=waveform)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 10) if self.voice else 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.performer is not None else 0
        flags |= (1 << 2) if self.waveform is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.duration))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.performer is not None:
            data.write(String(self.performer))
        
        if self.waveform is not None:
            data.write(Bytes(self.waveform))
        
        return data.getvalue()
