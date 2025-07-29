from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StatsDateRangeDays(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsDateRangeDays`.

    Details:
        - Layer: ``135``
        - ID: ``-0x49c81251``

    Parameters:
        min_date: ``int`` ``32-bit``
        max_date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["min_date", "max_date"]

    ID = -0x49c81251
    QUALNAME = "types.StatsDateRangeDays"

    def __init__(self, *, min_date: int, max_date: int) -> None:
        self.min_date = min_date  # int
        self.max_date = max_date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        min_date = Int.read(data)
        
        max_date = Int.read(data)
        
        return StatsDateRangeDays(min_date=min_date, max_date=max_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.min_date))
        
        data.write(Int(self.max_date))
        
        return data.getvalue()
