from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class DraftMessageEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DraftMessage`.

    Details:
        - Layer: ``135``
        - ID: ``0x1b0c841a``

    Parameters:
        date (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["date"]

    ID = 0x1b0c841a
    QUALNAME = "types.DraftMessageEmpty"

    def __init__(self, *, date: Optional[int] = None) -> None:
        self.date = date  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        date = Int.read(data) if flags & (1 << 0) else None
        return DraftMessageEmpty(date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.date is not None else 0
        data.write(Int(flags))
        
        if self.date is not None:
            data.write(Int(self.date))
        
        return data.getvalue()
