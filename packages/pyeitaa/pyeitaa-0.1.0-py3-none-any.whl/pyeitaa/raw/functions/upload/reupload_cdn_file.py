from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ReuploadCdnFile(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x64d8ab58``

    Parameters:
        file_token: ``bytes``
        request_token: ``bytes``

    Returns:
        List of :obj:`FileHash <pyeitaa.raw.base.FileHash>`
    """

    __slots__: List[str] = ["file_token", "request_token"]

    ID = -0x64d8ab58
    QUALNAME = "functions.upload.ReuploadCdnFile"

    def __init__(self, *, file_token: bytes, request_token: bytes) -> None:
        self.file_token = file_token  # bytes
        self.request_token = request_token  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        file_token = Bytes.read(data)
        
        request_token = Bytes.read(data)
        
        return ReuploadCdnFile(file_token=file_token, request_token=request_token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.file_token))
        
        data.write(Bytes(self.request_token))
        
        return data.getvalue()
