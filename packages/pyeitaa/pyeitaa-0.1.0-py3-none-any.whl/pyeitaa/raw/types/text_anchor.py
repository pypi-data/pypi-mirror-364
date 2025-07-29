from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TextAnchor(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RichText`.

    Details:
        - Layer: ``135``
        - ID: ``0x35553762``

    Parameters:
        text: :obj:`RichText <pyeitaa.raw.base.RichText>`
        name: ``str``
    """

    __slots__: List[str] = ["text", "name"]

    ID = 0x35553762
    QUALNAME = "types.TextAnchor"

    def __init__(self, *, text: "raw.base.RichText", name: str) -> None:
        self.text = text  # RichText
        self.name = name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = TLObject.read(data)
        
        name = String.read(data)
        
        return TextAnchor(text=text, name=name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.text.write())
        
        data.write(String(self.name))
        
        return data.getvalue()
