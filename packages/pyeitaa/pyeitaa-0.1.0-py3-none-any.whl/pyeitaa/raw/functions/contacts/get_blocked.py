from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetBlocked(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xa83caf1``

    Parameters:
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`contacts.Blocked <pyeitaa.raw.base.contacts.Blocked>`
    """

    __slots__: List[str] = ["offset", "limit"]

    ID = -0xa83caf1
    QUALNAME = "functions.contacts.GetBlocked"

    def __init__(self, *, offset: int, limit: int) -> None:
        self.offset = offset  # int
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offset = Int.read(data)
        
        limit = Int.read(data)
        
        return GetBlocked(offset=offset, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.offset))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
