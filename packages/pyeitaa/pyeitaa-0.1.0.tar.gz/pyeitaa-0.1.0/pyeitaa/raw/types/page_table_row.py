from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageTableRow(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageTableRow`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1f3f3a1b``

    Parameters:
        cells: List of :obj:`PageTableCell <pyeitaa.raw.base.PageTableCell>`
    """

    __slots__: List[str] = ["cells"]

    ID = -0x1f3f3a1b
    QUALNAME = "types.PageTableRow"

    def __init__(self, *, cells: List["raw.base.PageTableCell"]) -> None:
        self.cells = cells  # Vector<PageTableCell>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        cells = TLObject.read(data)
        
        return PageTableRow(cells=cells)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.cells))
        
        return data.getvalue()
