from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageListOrderedItemText(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageListOrderedItem`.

    Details:
        - Layer: ``135``
        - ID: ``0x5e068047``

    Parameters:
        num: ``str``
        text: :obj:`RichText <pyeitaa.raw.base.RichText>`
    """

    __slots__: List[str] = ["num", "text"]

    ID = 0x5e068047
    QUALNAME = "types.PageListOrderedItemText"

    def __init__(self, *, num: str, text: "raw.base.RichText") -> None:
        self.num = num  # string
        self.text = text  # RichText

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        num = String.read(data)
        
        text = TLObject.read(data)
        
        return PageListOrderedItemText(num=num, text=text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.num))
        
        data.write(self.text.write())
        
        return data.getvalue()
