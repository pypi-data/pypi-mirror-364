from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class PageBlockDetails(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``0x76768bed``

    Parameters:
        blocks: List of :obj:`PageBlock <pyeitaa.raw.base.PageBlock>`
        title: :obj:`RichText <pyeitaa.raw.base.RichText>`
        open (optional): ``bool``
    """

    __slots__: List[str] = ["blocks", "title", "open"]

    ID = 0x76768bed
    QUALNAME = "types.PageBlockDetails"

    def __init__(self, *, blocks: List["raw.base.PageBlock"], title: "raw.base.RichText", open: Optional[bool] = None) -> None:
        self.blocks = blocks  # Vector<PageBlock>
        self.title = title  # RichText
        self.open = open  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        open = True if flags & (1 << 0) else False
        blocks = TLObject.read(data)
        
        title = TLObject.read(data)
        
        return PageBlockDetails(blocks=blocks, title=title, open=open)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.open else 0
        data.write(Int(flags))
        
        data.write(Vector(self.blocks))
        
        data.write(self.title.write())
        
        return data.getvalue()
