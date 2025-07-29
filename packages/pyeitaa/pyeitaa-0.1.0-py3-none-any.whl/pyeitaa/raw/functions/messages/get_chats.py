from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetChats(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x49e9528f``

    Parameters:
        id: List of ``int`` ``64-bit``

    Returns:
        :obj:`messages.Chats <pyeitaa.raw.base.messages.Chats>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x49e9528f
    QUALNAME = "functions.messages.GetChats"

    def __init__(self, *, id: List[int]) -> None:
        self.id = id  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data, Long)
        
        return GetChats(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.id, Long))
        
        return data.getvalue()
