from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetLeftChannels(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x7cbe1340``

    Parameters:
        offset: ``int`` ``32-bit``

    Returns:
        :obj:`messages.Chats <pyeitaa.raw.base.messages.Chats>`
    """

    __slots__: List[str] = ["offset"]

    ID = -0x7cbe1340
    QUALNAME = "functions.channels.GetLeftChannels"

    def __init__(self, *, offset: int) -> None:
        self.offset = offset  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offset = Int.read(data)
        
        return GetLeftChannels(offset=offset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.offset))
        
        return data.getvalue()
