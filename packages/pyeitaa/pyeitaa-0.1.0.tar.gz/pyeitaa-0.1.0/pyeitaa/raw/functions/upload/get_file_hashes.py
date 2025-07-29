from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetFileHashes(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x38fda6cf``

    Parameters:
        location: :obj:`InputFileLocation <pyeitaa.raw.base.InputFileLocation>`
        offset: ``int`` ``32-bit``

    Returns:
        List of :obj:`FileHash <pyeitaa.raw.base.FileHash>`
    """

    __slots__: List[str] = ["location", "offset"]

    ID = -0x38fda6cf
    QUALNAME = "functions.upload.GetFileHashes"

    def __init__(self, *, location: "raw.base.InputFileLocation", offset: int) -> None:
        self.location = location  # InputFileLocation
        self.offset = offset  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        location = TLObject.read(data)
        
        offset = Int.read(data)
        
        return GetFileHashes(location=location, offset=offset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.location.write())
        
        data.write(Int(self.offset))
        
        return data.getvalue()
