from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockBlockquote(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``0x263d7c26``

    Parameters:
        text: :obj:`RichText <pyeitaa.raw.base.RichText>`
        caption: :obj:`RichText <pyeitaa.raw.base.RichText>`
    """

    __slots__: List[str] = ["text", "caption"]

    ID = 0x263d7c26
    QUALNAME = "types.PageBlockBlockquote"

    def __init__(self, *, text: "raw.base.RichText", caption: "raw.base.RichText") -> None:
        self.text = text  # RichText
        self.caption = caption  # RichText

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = TLObject.read(data)
        
        caption = TLObject.read(data)
        
        return PageBlockBlockquote(text=text, caption=caption)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.text.write())
        
        data.write(self.caption.write())
        
        return data.getvalue()
