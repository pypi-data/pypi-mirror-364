from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PageTableCell(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageTableCell`.

    Details:
        - Layer: ``135``
        - ID: ``0x34566b6a``

    Parameters:
        header (optional): ``bool``
        align_center (optional): ``bool``
        align_right (optional): ``bool``
        valign_middle (optional): ``bool``
        valign_bottom (optional): ``bool``
        text (optional): :obj:`RichText <pyeitaa.raw.base.RichText>`
        colspan (optional): ``int`` ``32-bit``
        rowspan (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["header", "align_center", "align_right", "valign_middle", "valign_bottom", "text", "colspan", "rowspan"]

    ID = 0x34566b6a
    QUALNAME = "types.PageTableCell"

    def __init__(self, *, header: Optional[bool] = None, align_center: Optional[bool] = None, align_right: Optional[bool] = None, valign_middle: Optional[bool] = None, valign_bottom: Optional[bool] = None, text: "raw.base.RichText" = None, colspan: Optional[int] = None, rowspan: Optional[int] = None) -> None:
        self.header = header  # flags.0?true
        self.align_center = align_center  # flags.3?true
        self.align_right = align_right  # flags.4?true
        self.valign_middle = valign_middle  # flags.5?true
        self.valign_bottom = valign_bottom  # flags.6?true
        self.text = text  # flags.7?RichText
        self.colspan = colspan  # flags.1?int
        self.rowspan = rowspan  # flags.2?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        header = True if flags & (1 << 0) else False
        align_center = True if flags & (1 << 3) else False
        align_right = True if flags & (1 << 4) else False
        valign_middle = True if flags & (1 << 5) else False
        valign_bottom = True if flags & (1 << 6) else False
        text = TLObject.read(data) if flags & (1 << 7) else None
        
        colspan = Int.read(data) if flags & (1 << 1) else None
        rowspan = Int.read(data) if flags & (1 << 2) else None
        return PageTableCell(header=header, align_center=align_center, align_right=align_right, valign_middle=valign_middle, valign_bottom=valign_bottom, text=text, colspan=colspan, rowspan=rowspan)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.header else 0
        flags |= (1 << 3) if self.align_center else 0
        flags |= (1 << 4) if self.align_right else 0
        flags |= (1 << 5) if self.valign_middle else 0
        flags |= (1 << 6) if self.valign_bottom else 0
        flags |= (1 << 7) if self.text is not None else 0
        flags |= (1 << 1) if self.colspan is not None else 0
        flags |= (1 << 2) if self.rowspan is not None else 0
        data.write(Int(flags))
        
        if self.text is not None:
            data.write(self.text.write())
        
        if self.colspan is not None:
            data.write(Int(self.colspan))
        
        if self.rowspan is not None:
            data.write(Int(self.rowspan))
        
        return data.getvalue()
