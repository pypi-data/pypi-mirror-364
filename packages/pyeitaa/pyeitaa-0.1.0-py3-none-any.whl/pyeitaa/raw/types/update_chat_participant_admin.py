from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bool
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateChatParticipantAdmin(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x28359e5e``

    Parameters:
        chat_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        is_admin: ``bool``
        version: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["chat_id", "user_id", "is_admin", "version"]

    ID = -0x28359e5e
    QUALNAME = "types.UpdateChatParticipantAdmin"

    def __init__(self, *, chat_id: int, user_id: int, is_admin: bool, version: int) -> None:
        self.chat_id = chat_id  # long
        self.user_id = user_id  # long
        self.is_admin = is_admin  # Bool
        self.version = version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        user_id = Long.read(data)
        
        is_admin = Bool.read(data)
        
        version = Int.read(data)
        
        return UpdateChatParticipantAdmin(chat_id=chat_id, user_id=user_id, is_admin=is_admin, version=version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(Long(self.user_id))
        
        data.write(Bool(self.is_admin))
        
        data.write(Int(self.version))
        
        return data.getvalue()
