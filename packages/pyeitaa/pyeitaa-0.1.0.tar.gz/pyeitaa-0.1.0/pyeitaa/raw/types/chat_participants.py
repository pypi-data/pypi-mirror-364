from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatParticipants(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatParticipants`.

    Details:
        - Layer: ``135``
        - ID: ``0x3cbc93f8``

    Parameters:
        chat_id: ``int`` ``64-bit``
        participants: List of :obj:`ChatParticipant <pyeitaa.raw.base.ChatParticipant>`
        version: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["chat_id", "participants", "version"]

    ID = 0x3cbc93f8
    QUALNAME = "types.ChatParticipants"

    def __init__(self, *, chat_id: int, participants: List["raw.base.ChatParticipant"], version: int) -> None:
        self.chat_id = chat_id  # long
        self.participants = participants  # Vector<ChatParticipant>
        self.version = version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        participants = TLObject.read(data)
        
        version = Int.read(data)
        
        return ChatParticipants(chat_id=chat_id, participants=participants, version=version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(Vector(self.participants))
        
        data.write(Int(self.version))
        
        return data.getvalue()
