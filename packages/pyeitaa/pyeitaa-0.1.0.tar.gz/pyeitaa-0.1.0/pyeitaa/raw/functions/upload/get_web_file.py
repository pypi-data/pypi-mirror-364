from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetWebFile(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x24e6818d``

    Parameters:
        location: :obj:`InputWebFileLocation <pyeitaa.raw.base.InputWebFileLocation>`
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`upload.WebFile <pyeitaa.raw.base.upload.WebFile>`
    """

    __slots__: List[str] = ["location", "offset", "limit"]

    ID = 0x24e6818d
    QUALNAME = "functions.upload.GetWebFile"

    def __init__(self, *, location: "raw.base.InputWebFileLocation", offset: int, limit: int) -> None:
        self.location = location  # InputWebFileLocation
        self.offset = offset  # int
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        location = TLObject.read(data)
        
        offset = Int.read(data)
        
        limit = Int.read(data)
        
        return GetWebFile(location=location, offset=offset, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.location.write())
        
        data.write(Int(self.offset))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
