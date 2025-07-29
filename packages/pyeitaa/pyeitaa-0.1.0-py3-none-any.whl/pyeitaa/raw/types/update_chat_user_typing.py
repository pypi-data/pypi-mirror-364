from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateChatUserTyping(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7cb78510``

    Parameters:
        chat_id: ``int`` ``64-bit``
        from_id: :obj:`Peer <pyeitaa.raw.base.Peer>`
        action: :obj:`SendMessageAction <pyeitaa.raw.base.SendMessageAction>`
    """

    __slots__: List[str] = ["chat_id", "from_id", "action"]

    ID = -0x7cb78510
    QUALNAME = "types.UpdateChatUserTyping"

    def __init__(self, *, chat_id: int, from_id: "raw.base.Peer", action: "raw.base.SendMessageAction") -> None:
        self.chat_id = chat_id  # long
        self.from_id = from_id  # Peer
        self.action = action  # SendMessageAction

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        from_id = TLObject.read(data)
        
        action = TLObject.read(data)
        
        return UpdateChatUserTyping(chat_id=chat_id, from_id=from_id, action=action)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(self.from_id.write())
        
        data.write(self.action.write())
        
        return data.getvalue()
