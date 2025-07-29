from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DifferenceEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.updates.Difference`.

    Details:
        - Layer: ``135``
        - ID: ``0x5d75a138``

    Parameters:
        date: ``int`` ``32-bit``
        seq: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetDifference <pyeitaa.raw.functions.updates.GetDifference>`
    """

    __slots__: List[str] = ["date", "seq"]

    ID = 0x5d75a138
    QUALNAME = "types.updates.DifferenceEmpty"

    def __init__(self, *, date: int, seq: int) -> None:
        self.date = date  # int
        self.seq = seq  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        date = Int.read(data)
        
        seq = Int.read(data)
        
        return DifferenceEmpty(date=date, seq=seq)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.date))
        
        data.write(Int(self.seq))
        
        return data.getvalue()
