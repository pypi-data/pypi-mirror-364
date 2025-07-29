from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockCollage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``0x65a0fa4d``

    Parameters:
        items: List of :obj:`PageBlock <pyeitaa.raw.base.PageBlock>`
        caption: :obj:`PageCaption <pyeitaa.raw.base.PageCaption>`
    """

    __slots__: List[str] = ["items", "caption"]

    ID = 0x65a0fa4d
    QUALNAME = "types.PageBlockCollage"

    def __init__(self, *, items: List["raw.base.PageBlock"], caption: "raw.base.PageCaption") -> None:
        self.items = items  # Vector<PageBlock>
        self.caption = caption  # PageCaption

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        items = TLObject.read(data)
        
        caption = TLObject.read(data)
        
        return PageBlockCollage(items=items, caption=caption)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.items))
        
        data.write(self.caption.write())
        
        return data.getvalue()
