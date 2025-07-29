from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ChannelParticipantsMentions(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelParticipantsFilter`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1fb4a315``

    Parameters:
        q (optional): ``str``
        top_msg_id (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["q", "top_msg_id"]

    ID = -0x1fb4a315
    QUALNAME = "types.ChannelParticipantsMentions"

    def __init__(self, *, q: Optional[str] = None, top_msg_id: Optional[int] = None) -> None:
        self.q = q  # flags.0?string
        self.top_msg_id = top_msg_id  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        q = String.read(data) if flags & (1 << 0) else None
        top_msg_id = Int.read(data) if flags & (1 << 1) else None
        return ChannelParticipantsMentions(q=q, top_msg_id=top_msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.q is not None else 0
        flags |= (1 << 1) if self.top_msg_id is not None else 0
        data.write(Int(flags))
        
        if self.q is not None:
            data.write(String(self.q))
        
        if self.top_msg_id is not None:
            data.write(Int(self.top_msg_id))
        
        return data.getvalue()
