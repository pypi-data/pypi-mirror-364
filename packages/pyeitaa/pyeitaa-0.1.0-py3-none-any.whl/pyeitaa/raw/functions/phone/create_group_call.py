from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class CreateGroupCall(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x48cdc6d8``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        random_id: ``int`` ``32-bit``
        title (optional): ``str``
        schedule_date (optional): ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "random_id", "title", "schedule_date"]

    ID = 0x48cdc6d8
    QUALNAME = "functions.phone.CreateGroupCall"

    def __init__(self, *, peer: "raw.base.InputPeer", random_id: int, title: Optional[str] = None, schedule_date: Optional[int] = None) -> None:
        self.peer = peer  # InputPeer
        self.random_id = random_id  # int
        self.title = title  # flags.0?string
        self.schedule_date = schedule_date  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        peer = TLObject.read(data)
        
        random_id = Int.read(data)
        
        title = String.read(data) if flags & (1 << 0) else None
        schedule_date = Int.read(data) if flags & (1 << 1) else None
        return CreateGroupCall(peer=peer, random_id=random_id, title=title, schedule_date=schedule_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.schedule_date is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.random_id))
        
        if self.title is not None:
            data.write(String(self.title))
        
        if self.schedule_date is not None:
            data.write(Int(self.schedule_date))
        
        return data.getvalue()
