from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SetTyping(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x58943ee2``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        action: :obj:`SendMessageAction <pyeitaa.raw.base.SendMessageAction>`
        top_msg_id (optional): ``int`` ``32-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "action", "top_msg_id"]

    ID = 0x58943ee2
    QUALNAME = "functions.messages.SetTyping"

    def __init__(self, *, peer: "raw.base.InputPeer", action: "raw.base.SendMessageAction", top_msg_id: Optional[int] = None) -> None:
        self.peer = peer  # InputPeer
        self.action = action  # SendMessageAction
        self.top_msg_id = top_msg_id  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        peer = TLObject.read(data)
        
        top_msg_id = Int.read(data) if flags & (1 << 0) else None
        action = TLObject.read(data)
        
        return SetTyping(peer=peer, action=action, top_msg_id=top_msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.top_msg_id is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        if self.top_msg_id is not None:
            data.write(Int(self.top_msg_id))
        
        data.write(self.action.write())
        
        return data.getvalue()
