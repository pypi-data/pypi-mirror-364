from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetCdnFile(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x2000bcc3``

    Parameters:
        file_token: ``bytes``
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`upload.CdnFile <pyeitaa.raw.base.upload.CdnFile>`
    """

    __slots__: List[str] = ["file_token", "offset", "limit"]

    ID = 0x2000bcc3
    QUALNAME = "functions.upload.GetCdnFile"

    def __init__(self, *, file_token: bytes, offset: int, limit: int) -> None:
        self.file_token = file_token  # bytes
        self.offset = offset  # int
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        file_token = Bytes.read(data)
        
        offset = Int.read(data)
        
        limit = Int.read(data)
        
        return GetCdnFile(file_token=file_token, offset=offset, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.file_token))
        
        data.write(Int(self.offset))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
