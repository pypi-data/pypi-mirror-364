from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EditChatTitle(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x73783ffd``

    Parameters:
        chat_id: ``int`` ``64-bit``
        title: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["chat_id", "title"]

    ID = 0x73783ffd
    QUALNAME = "functions.messages.EditChatTitle"

    def __init__(self, *, chat_id: int, title: str) -> None:
        self.chat_id = chat_id  # long
        self.title = title  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Long.read(data)
        
        title = String.read(data)
        
        return EditChatTitle(chat_id=chat_id, title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.chat_id))
        
        data.write(String(self.title))
        
        return data.getvalue()
