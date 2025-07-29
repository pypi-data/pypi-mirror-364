from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ReadFeaturedStickers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x5b118126``

    Parameters:
        id: List of ``int`` ``64-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id"]

    ID = 0x5b118126
    QUALNAME = "functions.messages.ReadFeaturedStickers"

    def __init__(self, *, id: List[int]) -> None:
        self.id = id  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data, Long)
        
        return ReadFeaturedStickers(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.id, Long))
        
        return data.getvalue()
