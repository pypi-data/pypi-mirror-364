from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class DeleteChatUser(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5de7a355``

    Parameters:
        chat_id: ``int`` ``64-bit``
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        revoke_history (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["chat_id", "user_id", "revoke_history"]

    ID = -0x5de7a355
    QUALNAME = "functions.messages.DeleteChatUser"

    def __init__(self, *, chat_id: int, user_id: "raw.base.InputUser", revoke_history: Optional[bool] = None) -> None:
        self.chat_id = chat_id  # long
        self.user_id = user_id  # InputUser
        self.revoke_history = revoke_history  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        revoke_history = True if flags & (1 << 0) else False
        chat_id = Long.read(data)
        
        user_id = TLObject.read(data)
        
        return DeleteChatUser(chat_id=chat_id, user_id=user_id, revoke_history=revoke_history)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.revoke_history else 0
        data.write(Int(flags))
        
        data.write(Long(self.chat_id))
        
        data.write(self.user_id.write())
        
        return data.getvalue()
