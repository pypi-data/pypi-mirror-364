from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TextPhone(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RichText`.

    Details:
        - Layer: ``135``
        - ID: ``0x1ccb966a``

    Parameters:
        text: :obj:`RichText <pyeitaa.raw.base.RichText>`
        phone: ``str``
    """

    __slots__: List[str] = ["text", "phone"]

    ID = 0x1ccb966a
    QUALNAME = "types.TextPhone"

    def __init__(self, *, text: "raw.base.RichText", phone: str) -> None:
        self.text = text  # RichText
        self.phone = phone  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = TLObject.read(data)
        
        phone = String.read(data)
        
        return TextPhone(text=text, phone=phone)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.text.write())
        
        data.write(String(self.phone))
        
        return data.getvalue()
