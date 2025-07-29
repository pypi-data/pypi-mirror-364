from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockList(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1b177fef``

    Parameters:
        items: List of :obj:`PageListItem <pyeitaa.raw.base.PageListItem>`
    """

    __slots__: List[str] = ["items"]

    ID = -0x1b177fef
    QUALNAME = "types.PageBlockList"

    def __init__(self, *, items: List["raw.base.PageListItem"]) -> None:
        self.items = items  # Vector<PageListItem>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        items = TLObject.read(data)
        
        return PageBlockList(items=items)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.items))
        
        return data.getvalue()
