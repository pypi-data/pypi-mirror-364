from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageListItemBlocks(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageListItem`.

    Details:
        - Layer: ``135``
        - ID: ``0x25e073fc``

    Parameters:
        blocks: List of :obj:`PageBlock <pyeitaa.raw.base.PageBlock>`
    """

    __slots__: List[str] = ["blocks"]

    ID = 0x25e073fc
    QUALNAME = "types.PageListItemBlocks"

    def __init__(self, *, blocks: List["raw.base.PageBlock"]) -> None:
        self.blocks = blocks  # Vector<PageBlock>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        blocks = TLObject.read(data)
        
        return PageListItemBlocks(blocks=blocks)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.blocks))
        
        return data.getvalue()
