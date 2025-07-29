from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class UpdateChannelTooLong(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x108d941f``

    Parameters:
        channel_id: ``int`` ``64-bit``
        pts (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "pts"]

    ID = 0x108d941f
    QUALNAME = "types.UpdateChannelTooLong"

    def __init__(self, *, channel_id: int, pts: Optional[int] = None) -> None:
        self.channel_id = channel_id  # long
        self.pts = pts  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        channel_id = Long.read(data)
        
        pts = Int.read(data) if flags & (1 << 0) else None
        return UpdateChannelTooLong(channel_id=channel_id, pts=pts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.pts is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.channel_id))
        
        if self.pts is not None:
            data.write(Int(self.pts))
        
        return data.getvalue()
