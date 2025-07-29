from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateChatParticipant(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2f7899c6``

    Parameters:
        chat_id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        actor_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        qts: ``int`` ``32-bit``
        prev_participant (optional): :obj:`ChatParticipant <pyeitaa.raw.base.ChatParticipant>`
        new_participant (optional): :obj:`ChatParticipant <pyeitaa.raw.base.ChatParticipant>`
        invite (optional): :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
    """

    __slots__: List[str] = ["chat_id", "date", "actor_id", "user_id", "qts", "prev_participant", "new_participant", "invite"]

    ID = -0x2f7899c6
    QUALNAME = "types.UpdateChatParticipant"

    def __init__(self, *, chat_id: int, date: int, actor_id: int, user_id: int, qts: int, prev_participant: "raw.base.ChatParticipant" = None, new_participant: "raw.base.ChatParticipant" = None, invite: "raw.base.ExportedChatInvite" = None) -> None:
        self.chat_id = chat_id  # long
        self.date = date  # int
        self.actor_id = actor_id  # long
        self.user_id = user_id  # long
        self.qts = qts  # int
        self.prev_participant = prev_participant  # flags.0?ChatParticipant
        self.new_participant = new_participant  # flags.1?ChatParticipant
        self.invite = invite  # flags.2?ExportedChatInvite

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        chat_id = Long.read(data)
        
        date = Int.read(data)
        
        actor_id = Long.read(data)
        
        user_id = Long.read(data)
        
        prev_participant = TLObject.read(data) if flags & (1 << 0) else None
        
        new_participant = TLObject.read(data) if flags & (1 << 1) else None
        
        invite = TLObject.read(data) if flags & (1 << 2) else None
        
        qts = Int.read(data)
        
        return UpdateChatParticipant(chat_id=chat_id, date=date, actor_id=actor_id, user_id=user_id, qts=qts, prev_participant=prev_participant, new_participant=new_participant, invite=invite)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.prev_participant is not None else 0
        flags |= (1 << 1) if self.new_participant is not None else 0
        flags |= (1 << 2) if self.invite is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.chat_id))
        
        data.write(Int(self.date))
        
        data.write(Long(self.actor_id))
        
        data.write(Long(self.user_id))
        
        if self.prev_participant is not None:
            data.write(self.prev_participant.write())
        
        if self.new_participant is not None:
            data.write(self.new_participant.write())
        
        if self.invite is not None:
            data.write(self.invite.write())
        
        data.write(Int(self.qts))
        
        return data.getvalue()
