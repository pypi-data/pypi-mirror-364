from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockPreformatted(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3f8f26c2``

    Parameters:
        text: :obj:`RichText <pyeitaa.raw.base.RichText>`
        language: ``str``
    """

    __slots__: List[str] = ["text", "language"]

    ID = -0x3f8f26c2
    QUALNAME = "types.PageBlockPreformatted"

    def __init__(self, *, text: "raw.base.RichText", language: str) -> None:
        self.text = text  # RichText
        self.language = language  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = TLObject.read(data)
        
        language = String.read(data)
        
        return PageBlockPreformatted(text=text, language=language)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.text.write())
        
        data.write(String(self.language))
        
        return data.getvalue()
