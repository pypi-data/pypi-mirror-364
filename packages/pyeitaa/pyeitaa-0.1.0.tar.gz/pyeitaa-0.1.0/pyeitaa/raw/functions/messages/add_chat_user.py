from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AddChatUser(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xdb8ac1d``

    Parameters:
        chat_id: ``int`` ``64-bit``
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        fwd_limit: ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["chat_id", "user_id", "fwd_limit"]

    ID = -0xdb8ac1d
    QUALNAME = "functions.messages.AddChatUser"

    def __init__(self, *, chat_id: int, user_id: "raw.base.InputUser", fwd_limit: int) -> None:
        self.chat_id = chat_id  # long
        self.user_id = user_id  # InputUser
        self.fwd_limit = fwd_limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        user_id = TLObject.read(data)
        
        fwd_limit = Int.read(data)
        
        return AddChatUser(chat_id=chat_id, user_id=user_id, fwd_limit=fwd_limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(self.user_id.write())
        
        data.write(Int(self.fwd_limit))
        
        return data.getvalue()
