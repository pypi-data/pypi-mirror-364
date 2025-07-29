from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Double
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StatsAbsValueAndPrev(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsAbsValueAndPrev`.

    Details:
        - Layer: ``135``
        - ID: ``-0x34bc5322``

    Parameters:
        current: ``float`` ``64-bit``
        previous: ``float`` ``64-bit``
    """

    __slots__: List[str] = ["current", "previous"]

    ID = -0x34bc5322
    QUALNAME = "types.StatsAbsValueAndPrev"

    def __init__(self, *, current: float, previous: float) -> None:
        self.current = current  # double
        self.previous = previous  # double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        current = Double.read(data)
        
        previous = Double.read(data)
        
        return StatsAbsValueAndPrev(current=current, previous=previous)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Double(self.current))
        
        data.write(Double(self.previous))
        
        return data.getvalue()
