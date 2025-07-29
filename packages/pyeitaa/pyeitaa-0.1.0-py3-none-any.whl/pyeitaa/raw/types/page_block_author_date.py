from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockAuthorDate(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x45501a20``

    Parameters:
        author: :obj:`RichText <pyeitaa.raw.base.RichText>`
        published_date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["author", "published_date"]

    ID = -0x45501a20
    QUALNAME = "types.PageBlockAuthorDate"

    def __init__(self, *, author: "raw.base.RichText", published_date: int) -> None:
        self.author = author  # RichText
        self.published_date = published_date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        author = TLObject.read(data)
        
        published_date = Int.read(data)
        
        return PageBlockAuthorDate(author=author, published_date=published_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.author.write())
        
        data.write(Int(self.published_date))
        
        return data.getvalue()
