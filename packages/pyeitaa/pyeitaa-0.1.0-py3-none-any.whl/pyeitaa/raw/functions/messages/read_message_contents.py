from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ReadMessageContents(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x36a73f77``

    Parameters:
        id: List of ``int`` ``32-bit``

    Returns:
        :obj:`messages.AffectedMessages <pyeitaa.raw.base.messages.AffectedMessages>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x36a73f77
    QUALNAME = "functions.messages.ReadMessageContents"

    def __init__(self, *, id: List[int]) -> None:
        self.id = id  # Vector<int>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data, Int)
        
        return ReadMessageContents(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.id, Int))
        
        return data.getvalue()
