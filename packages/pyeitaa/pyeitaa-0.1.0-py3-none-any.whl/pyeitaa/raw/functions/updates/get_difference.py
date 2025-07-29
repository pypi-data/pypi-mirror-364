from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class GetDifference(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x25939651``

    Parameters:
        pts: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
        qts: ``int`` ``32-bit``
        pts_total_limit (optional): ``int`` ``32-bit``

    Returns:
        :obj:`updates.Difference <pyeitaa.raw.base.updates.Difference>`
    """

    __slots__: List[str] = ["pts", "date", "qts", "pts_total_limit"]

    ID = 0x25939651
    QUALNAME = "functions.updates.GetDifference"

    def __init__(self, *, pts: int, date: int, qts: int, pts_total_limit: Optional[int] = None) -> None:
        self.pts = pts  # int
        self.date = date  # int
        self.qts = qts  # int
        self.pts_total_limit = pts_total_limit  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        pts = Int.read(data)
        
        pts_total_limit = Int.read(data) if flags & (1 << 0) else None
        date = Int.read(data)
        
        qts = Int.read(data)
        
        return GetDifference(pts=pts, date=date, qts=qts, pts_total_limit=pts_total_limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.pts_total_limit is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.pts))
        
        if self.pts_total_limit is not None:
            data.write(Int(self.pts_total_limit))
        
        data.write(Int(self.date))
        
        data.write(Int(self.qts))
        
        return data.getvalue()
