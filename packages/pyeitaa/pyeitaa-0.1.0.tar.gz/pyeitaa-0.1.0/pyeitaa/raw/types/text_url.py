from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class TextUrl(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RichText`.

    Details:
        - Layer: ``135``
        - ID: ``0x3c2884c1``

    Parameters:
        text: :obj:`RichText <pyeitaa.raw.base.RichText>`
        url: ``str``
        webpage_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["text", "url", "webpage_id"]

    ID = 0x3c2884c1
    QUALNAME = "types.TextUrl"

    def __init__(self, *, text: "raw.base.RichText", url: str, webpage_id: int) -> None:
        self.text = text  # RichText
        self.url = url  # string
        self.webpage_id = webpage_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = TLObject.read(data)
        
        url = String.read(data)
        
        webpage_id = Long.read(data)
        
        return TextUrl(text=text, url=url, webpage_id=webpage_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.text.write())
        
        data.write(String(self.url))
        
        data.write(Long(self.webpage_id))
        
        return data.getvalue()
