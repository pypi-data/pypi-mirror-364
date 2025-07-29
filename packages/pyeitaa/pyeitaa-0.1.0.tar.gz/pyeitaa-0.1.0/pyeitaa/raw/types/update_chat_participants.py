from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateChatParticipants(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x7761198``

    Parameters:
        participants: :obj:`ChatParticipants <pyeitaa.raw.base.ChatParticipants>`
    """

    __slots__: List[str] = ["participants"]

    ID = 0x7761198
    QUALNAME = "types.UpdateChatParticipants"

    def __init__(self, *, participants: "raw.base.ChatParticipants") -> None:
        self.participants = participants  # ChatParticipants

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        participants = TLObject.read(data)
        
        return UpdateChatParticipants(participants=participants)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.participants.write())
        
        return data.getvalue()
