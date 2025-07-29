from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ExportChatInviteLayer84(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x7d885289``

    Parameters:
        chat_id: ``int`` ``32-bit``

    Returns:
        :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
    """

    __slots__: List[str] = ["chat_id"]

    ID = 0x7d885289
    QUALNAME = "functions.messages.ExportChatInviteLayer84"

    def __init__(self, *, chat_id: int) -> None:
        self.chat_id = chat_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat_id = Int.read(data)
        
        return ExportChatInviteLayer84(chat_id=chat_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.chat_id))
        
        return data.getvalue()
