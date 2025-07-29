from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class Search(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x11f812d8``

    Parameters:
        q: ``str``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`contacts.Found <pyeitaa.raw.base.contacts.Found>`
    """

    __slots__: List[str] = ["q", "limit"]

    ID = 0x11f812d8
    QUALNAME = "functions.contacts.Search"

    def __init__(self, *, q: str, limit: int) -> None:
        self.q = q  # string
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        q = String.read(data)
        
        limit = Int.read(data)
        
        return Search(q=q, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.q))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
