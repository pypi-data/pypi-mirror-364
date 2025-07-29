from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetWebPage(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x32ca8f91``

    Parameters:
        url: ``str``
        hash: ``int`` ``32-bit``

    Returns:
        :obj:`WebPage <pyeitaa.raw.base.WebPage>`
    """

    __slots__: List[str] = ["url", "hash"]

    ID = 0x32ca8f91
    QUALNAME = "functions.messages.GetWebPage"

    def __init__(self, *, url: str, hash: int) -> None:
        self.url = url  # string
        self.hash = hash  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        hash = Int.read(data)
        
        return GetWebPage(url=url, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(Int(self.hash))
        
        return data.getvalue()
