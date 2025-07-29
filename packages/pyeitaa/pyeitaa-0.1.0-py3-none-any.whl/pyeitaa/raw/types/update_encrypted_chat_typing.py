from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateEncryptedChatTyping(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x1710f156``

    Parameters:
        chat_id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["chat_id"]

    ID = 0x1710f156
    QUALNAME = "types.UpdateEncryptedChatTyping"

    def __init__(self, *, chat_id: int) -> None:
        self.chat_id = chat_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Int.read(data)
        
        return UpdateEncryptedChatTyping(chat_id=chat_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.chat_id))
        
        return data.getvalue()
