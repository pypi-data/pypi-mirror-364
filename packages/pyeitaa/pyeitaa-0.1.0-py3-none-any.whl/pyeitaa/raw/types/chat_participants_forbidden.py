from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatParticipantsForbidden(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatParticipants`.

    Details:
        - Layer: ``135``
        - ID: ``-0x789c2c1f``

    Parameters:
        chat_id: ``int`` ``64-bit``
        self_participant (optional): :obj:`ChatParticipant <pyeitaa.raw.base.ChatParticipant>`
    """

    __slots__: List[str] = ["chat_id", "self_participant"]

    ID = -0x789c2c1f
    QUALNAME = "types.ChatParticipantsForbidden"

    def __init__(self, *, chat_id: int, self_participant: "raw.base.ChatParticipant" = None) -> None:
        self.chat_id = chat_id  # long
        self.self_participant = self_participant  # flags.0?ChatParticipant

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        chat_id = Long.read(data)
        
        self_participant = TLObject.read(data) if flags & (1 << 0) else None
        
        return ChatParticipantsForbidden(chat_id=chat_id, self_participant=self_participant)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.self_participant is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.chat_id))
        
        if self.self_participant is not None:
            data.write(self.self_participant.write())
        
        return data.getvalue()
