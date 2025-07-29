from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class DiscardEncryption(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xc6c5160``

    Parameters:
        chat_id: ``int`` ``32-bit``
        delete_history (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["chat_id", "delete_history"]

    ID = -0xc6c5160
    QUALNAME = "functions.messages.DiscardEncryption"

    def __init__(self, *, chat_id: int, delete_history: Optional[bool] = None) -> None:
        self.chat_id = chat_id  # int
        self.delete_history = delete_history  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        delete_history = True if flags & (1 << 0) else False
        chat_id = Int.read(data)
        
        return DiscardEncryption(chat_id=chat_id, delete_history=delete_history)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.delete_history else 0
        data.write(Int(flags))
        
        data.write(Int(self.chat_id))
        
        return data.getvalue()
