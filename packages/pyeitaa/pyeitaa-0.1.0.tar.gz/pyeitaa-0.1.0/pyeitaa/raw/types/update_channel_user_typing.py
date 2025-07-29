from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateChannelUserTyping(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x737736dd``

    Parameters:
        channel_id: ``int`` ``64-bit``
        from_id: :obj:`Peer <pyeitaa.raw.base.Peer>`
        action: :obj:`SendMessageAction <pyeitaa.raw.base.SendMessageAction>`
        top_msg_id (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "from_id", "action", "top_msg_id"]

    ID = -0x737736dd
    QUALNAME = "types.UpdateChannelUserTyping"

    def __init__(self, *, channel_id: int, from_id: "raw.base.Peer", action: "raw.base.SendMessageAction", top_msg_id: Optional[int] = None) -> None:
        self.channel_id = channel_id  # long
        self.from_id = from_id  # Peer
        self.action = action  # SendMessageAction
        self.top_msg_id = top_msg_id  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        channel_id = Long.read(data)
        
        top_msg_id = Int.read(data) if flags & (1 << 0) else None
        from_id = TLObject.read(data)
        
        action = TLObject.read(data)
        
        return UpdateChannelUserTyping(channel_id=channel_id, from_id=from_id, action=action, top_msg_id=top_msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.top_msg_id is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.channel_id))
        
        if self.top_msg_id is not None:
            data.write(Int(self.top_msg_id))
        
        data.write(self.from_id.write())
        
        data.write(self.action.write())
        
        return data.getvalue()
