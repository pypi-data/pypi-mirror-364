from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetCdnFileHashes(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x4da54231``

    Parameters:
        file_token: ``bytes``
        offset: ``int`` ``32-bit``

    Returns:
        List of :obj:`FileHash <pyeitaa.raw.base.FileHash>`
    """

    __slots__: List[str] = ["file_token", "offset"]

    ID = 0x4da54231
    QUALNAME = "functions.upload.GetCdnFileHashes"

    def __init__(self, *, file_token: bytes, offset: int) -> None:
        self.file_token = file_token  # bytes
        self.offset = offset  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        file_token = Bytes.read(data)
        
        offset = Int.read(data)
        
        return GetCdnFileHashes(file_token=file_token, offset=offset)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.file_token))
        
        data.write(Int(self.offset))
        
        return data.getvalue()
