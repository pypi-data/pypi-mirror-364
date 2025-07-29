from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockOrderedList(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x65751e1f``

    Parameters:
        items: List of :obj:`PageListOrderedItem <pyeitaa.raw.base.PageListOrderedItem>`
    """

    __slots__: List[str] = ["items"]

    ID = -0x65751e1f
    QUALNAME = "types.PageBlockOrderedList"

    def __init__(self, *, items: List["raw.base.PageListOrderedItem"]) -> None:
        self.items = items  # Vector<PageListOrderedItem>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        items = TLObject.read(data)
        
        return PageBlockOrderedList(items=items)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.items))
        
        return data.getvalue()
