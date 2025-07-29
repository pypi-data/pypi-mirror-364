from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SaveDraft(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x43c61eb5``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        message: ``str``
        no_webpage (optional): ``bool``
        reply_to_msg_id (optional): ``int`` ``32-bit``
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "message", "no_webpage", "reply_to_msg_id", "entities"]

    ID = -0x43c61eb5
    QUALNAME = "functions.messages.SaveDraft"

    def __init__(self, *, peer: "raw.base.InputPeer", message: str, no_webpage: Optional[bool] = None, reply_to_msg_id: Optional[int] = None, entities: Optional[List["raw.base.MessageEntity"]] = None) -> None:
        self.peer = peer  # InputPeer
        self.message = message  # string
        self.no_webpage = no_webpage  # flags.1?true
        self.reply_to_msg_id = reply_to_msg_id  # flags.0?int
        self.entities = entities  # flags.3?Vector<MessageEntity>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        no_webpage = True if flags & (1 << 1) else False
        reply_to_msg_id = Int.read(data) if flags & (1 << 0) else None
        peer = TLObject.read(data)
        
        message = String.read(data)
        
        entities = TLObject.read(data) if flags & (1 << 3) else []
        
        return SaveDraft(peer=peer, message=message, no_webpage=no_webpage, reply_to_msg_id=reply_to_msg_id, entities=entities)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.no_webpage else 0
        flags |= (1 << 0) if self.reply_to_msg_id is not None else 0
        flags |= (1 << 3) if self.entities is not None else 0
        data.write(Int(flags))
        
        if self.reply_to_msg_id is not None:
            data.write(Int(self.reply_to_msg_id))
        
        data.write(self.peer.write())
        
        data.write(String(self.message))
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        return data.getvalue()
