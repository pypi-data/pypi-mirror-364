from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionChatJoinedByLink(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x31224c3``

    Parameters:
        inviter_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["inviter_id"]

    ID = 0x31224c3
    QUALNAME = "types.MessageActionChatJoinedByLink"

    def __init__(self, *, inviter_id: int) -> None:
        self.inviter_id = inviter_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        inviter_id = Long.read(data)
        
        return MessageActionChatJoinedByLink(inviter_id=inviter_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.inviter_id))
        
        return data.getvalue()
