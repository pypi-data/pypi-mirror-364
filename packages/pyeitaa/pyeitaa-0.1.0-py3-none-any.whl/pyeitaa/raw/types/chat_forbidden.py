from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChatForbidden(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Chat`.

    Details:
        - Layer: ``135``
        - ID: ``0x6592a1a7``

    Parameters:
        id: ``int`` ``64-bit``
        title: ``str``
    """

    __slots__: List[str] = ["id", "title"]

    ID = 0x6592a1a7
    QUALNAME = "types.ChatForbidden"

    def __init__(self, *, id: int, title: str) -> None:
        self.id = id  # long
        self.title = title  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        title = String.read(data)
        
        return ChatForbidden(id=id, title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(String(self.title))
        
        return data.getvalue()
