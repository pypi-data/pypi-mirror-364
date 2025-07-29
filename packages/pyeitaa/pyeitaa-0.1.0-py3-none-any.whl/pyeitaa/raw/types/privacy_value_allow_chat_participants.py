from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PrivacyValueAllowChatParticipants(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PrivacyRule`.

    Details:
        - Layer: ``135``
        - ID: ``0x6b134e8e``

    Parameters:
        chats: List of ``int`` ``64-bit``
    """

    __slots__: List[str] = ["chats"]

    ID = 0x6b134e8e
    QUALNAME = "types.PrivacyValueAllowChatParticipants"

    def __init__(self, *, chats: List[int]) -> None:
        self.chats = chats  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chats = TLObject.read(data, Long)
        
        return PrivacyValueAllowChatParticipants(chats=chats)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.chats, Long))
        
        return data.getvalue()
