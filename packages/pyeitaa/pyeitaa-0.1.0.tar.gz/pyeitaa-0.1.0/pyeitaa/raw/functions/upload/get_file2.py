from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetFile2(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1c59304b``

    Parameters:
        location: :obj:`InputFileLocation <pyeitaa.raw.base.InputFileLocation>`
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`upload.File <pyeitaa.raw.base.upload.File>`
    """

    __slots__: List[str] = ["location", "offset", "limit"]

    ID = -0x1c59304b
    QUALNAME = "functions.upload.GetFile2"

    def __init__(self, *, location: "raw.base.InputFileLocation", offset: int, limit: int) -> None:
        self.location = location  # InputFileLocation
        self.offset = offset  # int
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        location = TLObject.read(data)
        
        offset = Int.read(data)
        
        limit = Int.read(data)
        
        return GetFile2(location=location, offset=offset, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.location.write())
        
        data.write(Int(self.offset))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
