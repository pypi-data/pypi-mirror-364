from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetCommonChats(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1bf35efc``

    Parameters:
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        max_id: ``int`` ``64-bit``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`messages.Chats <pyeitaa.raw.base.messages.Chats>`
    """

    __slots__: List[str] = ["user_id", "max_id", "limit"]

    ID = -0x1bf35efc
    QUALNAME = "functions.messages.GetCommonChats"

    def __init__(self, *, user_id: "raw.base.InputUser", max_id: int, limit: int) -> None:
        self.user_id = user_id  # InputUser
        self.max_id = max_id  # long
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = TLObject.read(data)
        
        max_id = Long.read(data)
        
        limit = Int.read(data)
        
        return GetCommonChats(user_id=user_id, max_id=max_id, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.user_id.write())
        
        data.write(Long(self.max_id))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
