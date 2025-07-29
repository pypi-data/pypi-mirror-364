from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionChatEditTitle(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4a5e31a6``

    Parameters:
        title: ``str``
    """

    __slots__: List[str] = ["title"]

    ID = -0x4a5e31a6
    QUALNAME = "types.MessageActionChatEditTitle"

    def __init__(self, *, title: str) -> None:
        self.title = title  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        title = String.read(data)
        
        return MessageActionChatEditTitle(title=title)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.title))
        
        return data.getvalue()
