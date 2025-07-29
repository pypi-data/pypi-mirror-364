from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class TextImage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RichText`.

    Details:
        - Layer: ``135``
        - ID: ``0x81ccf4f``

    Parameters:
        document_id: ``int`` ``64-bit``
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["document_id", "w", "h"]

    ID = 0x81ccf4f
    QUALNAME = "types.TextImage"

    def __init__(self, *, document_id: int, w: int, h: int) -> None:
        self.document_id = document_id  # long
        self.w = w  # int
        self.h = h  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        document_id = Long.read(data)
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        return TextImage(document_id=document_id, w=w, h=h)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.document_id))
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        return data.getvalue()
