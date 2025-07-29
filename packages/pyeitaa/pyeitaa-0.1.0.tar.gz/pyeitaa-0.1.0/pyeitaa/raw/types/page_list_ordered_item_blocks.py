from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageListOrderedItemBlocks(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageListOrderedItem`.

    Details:
        - Layer: ``135``
        - ID: ``-0x672276ca``

    Parameters:
        num: ``str``
        blocks: List of :obj:`PageBlock <pyeitaa.raw.base.PageBlock>`
    """

    __slots__: List[str] = ["num", "blocks"]

    ID = -0x672276ca
    QUALNAME = "types.PageListOrderedItemBlocks"

    def __init__(self, *, num: str, blocks: List["raw.base.PageBlock"]) -> None:
        self.num = num  # string
        self.blocks = blocks  # Vector<PageBlock>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        num = String.read(data)
        
        blocks = TLObject.read(data)
        
        return PageListOrderedItemBlocks(num=num, blocks=blocks)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.num))
        
        data.write(Vector(self.blocks))
        
        return data.getvalue()
