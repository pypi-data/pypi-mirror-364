from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Double
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StatsPercentValue(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsPercentValue`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3431d020``

    Parameters:
        part: ``float`` ``64-bit``
        total: ``float`` ``64-bit``
    """

    __slots__: List[str] = ["part", "total"]

    ID = -0x3431d020
    QUALNAME = "types.StatsPercentValue"

    def __init__(self, *, part: float, total: float) -> None:
        self.part = part  # double
        self.total = total  # double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        part = Double.read(data)
        
        total = Double.read(data)
        
        return StatsPercentValue(part=part, total=total)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Double(self.part))
        
        data.write(Double(self.total))
        
        return data.getvalue()
