from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockCover(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``0x39f23300``

    Parameters:
        cover: :obj:`PageBlock <pyeitaa.raw.base.PageBlock>`
    """

    __slots__: List[str] = ["cover"]

    ID = 0x39f23300
    QUALNAME = "types.PageBlockCover"

    def __init__(self, *, cover: "raw.base.PageBlock") -> None:
        self.cover = cover  # PageBlock

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        cover = TLObject.read(data)
        
        return PageBlockCover(cover=cover)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.cover.write())
        
        return data.getvalue()
