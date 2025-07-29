from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputMessageID(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMessage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x59895cde``

    Parameters:
        id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id"]

    ID = -0x59895cde
    QUALNAME = "types.InputMessageID"

    def __init__(self, *, id: int) -> None:
        self.id = id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Int.read(data)
        
        return InputMessageID(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.id))
        
        return data.getvalue()
