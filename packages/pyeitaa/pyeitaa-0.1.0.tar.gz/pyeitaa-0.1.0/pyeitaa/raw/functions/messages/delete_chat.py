from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DeleteChat(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x5bd0ee50``

    Parameters:
        chat_id: ``int`` ``64-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["chat_id"]

    ID = 0x5bd0ee50
    QUALNAME = "functions.messages.DeleteChat"

    def __init__(self, *, chat_id: int) -> None:
        self.chat_id = chat_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        return DeleteChat(chat_id=chat_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        return data.getvalue()
