from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GroupCallParticipantVideo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.GroupCallParticipantVideo`.

    Details:
        - Layer: ``135``
        - ID: ``0x67753ac8``

    Parameters:
        endpoint: ``str``
        source_groups: List of :obj:`GroupCallParticipantVideoSourceGroup <pyeitaa.raw.base.GroupCallParticipantVideoSourceGroup>`
        paused (optional): ``bool``
        audio_source (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["endpoint", "source_groups", "paused", "audio_source"]

    ID = 0x67753ac8
    QUALNAME = "types.GroupCallParticipantVideo"

    def __init__(self, *, endpoint: str, source_groups: List["raw.base.GroupCallParticipantVideoSourceGroup"], paused: Optional[bool] = None, audio_source: Optional[int] = None) -> None:
        self.endpoint = endpoint  # string
        self.source_groups = source_groups  # Vector<GroupCallParticipantVideoSourceGroup>
        self.paused = paused  # flags.0?true
        self.audio_source = audio_source  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        paused = True if flags & (1 << 0) else False
        endpoint = String.read(data)
        
        source_groups = TLObject.read(data)
        
        audio_source = Int.read(data) if flags & (1 << 1) else None
        return GroupCallParticipantVideo(endpoint=endpoint, source_groups=source_groups, paused=paused, audio_source=audio_source)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.paused else 0
        flags |= (1 << 1) if self.audio_source is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.endpoint))
        
        data.write(Vector(self.source_groups))
        
        if self.audio_source is not None:
            data.write(Int(self.audio_source))
        
        return data.getvalue()
