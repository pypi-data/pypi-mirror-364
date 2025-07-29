from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TextEmail(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RichText`.

    Details:
        - Layer: ``135``
        - ID: ``-0x21a5f22a``

    Parameters:
        text: :obj:`RichText <pyeitaa.raw.base.RichText>`
        email: ``str``
    """

    __slots__: List[str] = ["text", "email"]

    ID = -0x21a5f22a
    QUALNAME = "types.TextEmail"

    def __init__(self, *, text: "raw.base.RichText", email: str) -> None:
        self.text = text  # RichText
        self.email = email  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = TLObject.read(data)
        
        email = String.read(data)
        
        return TextEmail(text=text, email=email)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.text.write())
        
        data.write(String(self.email))
        
        return data.getvalue()
