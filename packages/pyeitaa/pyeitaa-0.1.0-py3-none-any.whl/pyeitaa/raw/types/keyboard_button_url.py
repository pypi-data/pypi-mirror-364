from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class KeyboardButtonUrl(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.KeyboardButton`.

    Details:
        - Layer: ``135``
        - ID: ``0x258aff05``

    Parameters:
        text: ``str``
        url: ``str``
    """

    __slots__: List[str] = ["text", "url"]

    ID = 0x258aff05
    QUALNAME = "types.KeyboardButtonUrl"

    def __init__(self, *, text: str, url: str) -> None:
        self.text = text  # string
        self.url = url  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = String.read(data)
        
        url = String.read(data)
        
        return KeyboardButtonUrl(text=text, url=url)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.text))
        
        data.write(String(self.url))
        
        return data.getvalue()
