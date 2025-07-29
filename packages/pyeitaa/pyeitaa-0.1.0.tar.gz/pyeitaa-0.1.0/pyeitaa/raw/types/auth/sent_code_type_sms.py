from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SentCodeTypeSms(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.SentCodeType`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3fff445e``

    Parameters:
        length: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["length"]

    ID = -0x3fff445e
    QUALNAME = "types.auth.SentCodeTypeSms"

    def __init__(self, *, length: int) -> None:
        self.length = length  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        length = Int.read(data)
        
        return SentCodeTypeSms(length=length)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.length))
        
        return data.getvalue()
