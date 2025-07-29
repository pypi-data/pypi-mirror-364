from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageCaption(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageCaption`.

    Details:
        - Layer: ``135``
        - ID: ``0x6f747657``

    Parameters:
        text: :obj:`RichText <pyeitaa.raw.base.RichText>`
        credit: :obj:`RichText <pyeitaa.raw.base.RichText>`
    """

    __slots__: List[str] = ["text", "credit"]

    ID = 0x6f747657
    QUALNAME = "types.PageCaption"

    def __init__(self, *, text: "raw.base.RichText", credit: "raw.base.RichText") -> None:
        self.text = text  # RichText
        self.credit = credit  # RichText

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = TLObject.read(data)
        
        credit = TLObject.read(data)
        
        return PageCaption(text=text, credit=credit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.text.write())
        
        data.write(self.credit.write())
        
        return data.getvalue()
