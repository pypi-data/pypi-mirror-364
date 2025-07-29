from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DifferenceTooLong(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.updates.Difference`.

    Details:
        - Layer: ``135``
        - ID: ``0x4afe8f6d``

    Parameters:
        pts: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetDifference <pyeitaa.raw.functions.updates.GetDifference>`
    """

    __slots__: List[str] = ["pts"]

    ID = 0x4afe8f6d
    QUALNAME = "types.updates.DifferenceTooLong"

    def __init__(self, *, pts: int) -> None:
        self.pts = pts  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pts = Int.read(data)
        
        return DifferenceTooLong(pts=pts)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.pts))
        
        return data.getvalue()
