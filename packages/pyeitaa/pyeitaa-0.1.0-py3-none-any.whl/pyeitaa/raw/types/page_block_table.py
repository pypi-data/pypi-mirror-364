from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PageBlockTable(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x40b2157e``

    Parameters:
        title: :obj:`RichText <pyeitaa.raw.base.RichText>`
        rows: List of :obj:`PageTableRow <pyeitaa.raw.base.PageTableRow>`
        bordered (optional): ``bool``
        striped (optional): ``bool``
    """

    __slots__: List[str] = ["title", "rows", "bordered", "striped"]

    ID = -0x40b2157e
    QUALNAME = "types.PageBlockTable"

    def __init__(self, *, title: "raw.base.RichText", rows: List["raw.base.PageTableRow"], bordered: Optional[bool] = None, striped: Optional[bool] = None) -> None:
        self.title = title  # RichText
        self.rows = rows  # Vector<PageTableRow>
        self.bordered = bordered  # flags.0?true
        self.striped = striped  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        bordered = True if flags & (1 << 0) else False
        striped = True if flags & (1 << 1) else False
        title = TLObject.read(data)
        
        rows = TLObject.read(data)
        
        return PageBlockTable(title=title, rows=rows, bordered=bordered, striped=striped)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.bordered else 0
        flags |= (1 << 1) if self.striped else 0
        data.write(Int(flags))
        
        data.write(self.title.write())
        
        data.write(Vector(self.rows))
        
        return data.getvalue()
