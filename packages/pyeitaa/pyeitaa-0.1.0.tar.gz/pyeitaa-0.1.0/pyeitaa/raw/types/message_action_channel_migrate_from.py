from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionChannelMigrateFrom(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x15c6b717``

    Parameters:
        title: ``str``
        chat_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["title", "chat_id"]

    ID = -0x15c6b717
    QUALNAME = "types.MessageActionChannelMigrateFrom"

    def __init__(self, *, title: str, chat_id: int) -> None:
        self.title = title  # string
        self.chat_id = chat_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        title = String.read(data)
        
        chat_id = Long.read(data)
        
        return MessageActionChannelMigrateFrom(title=title, chat_id=chat_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.title))
        
        data.write(Long(self.chat_id))
        
        return data.getvalue()
