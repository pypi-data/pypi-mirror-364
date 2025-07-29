from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditChatAdmin(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x57a42e3e``

    Parameters:
        chat_id: ``int`` ``64-bit``
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        is_admin: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["chat_id", "user_id", "is_admin"]

    ID = -0x57a42e3e
    QUALNAME = "functions.messages.EditChatAdmin"

    def __init__(self, *, chat_id: int, user_id: "raw.base.InputUser", is_admin: bool) -> None:
        self.chat_id = chat_id  # long
        self.user_id = user_id  # InputUser
        self.is_admin = is_admin  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        user_id = TLObject.read(data)
        
        is_admin = Bool.read(data)
        
        return EditChatAdmin(chat_id=chat_id, user_id=user_id, is_admin=is_admin)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(self.user_id.write())
        
        data.write(Bool(self.is_admin))
        
        return data.getvalue()
