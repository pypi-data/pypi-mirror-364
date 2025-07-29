from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CrashReport(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1e91a7f7``

    Parameters:
        flags: ``int`` ``32-bit``
        body: ``bytes``
        uri: ``str``
        queryParams: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["flags", "body", "uri", "queryParams"]

    ID = 0x1e91a7f7
    QUALNAME = "functions.CrashReport"

    def __init__(self, *, flags: int, body: bytes, uri: str, queryParams: str) -> None:
        self.flags = flags  # int
        self.body = body  # bytes
        self.uri = uri  # string
        self.queryParams = queryParams  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        flags = Int.read(data)
        
        body = Bytes.read(data)
        
        uri = String.read(data)
        
        queryParams = String.read(data)
        
        return CrashReport(flags=flags, body=body, uri=uri, queryParams=queryParams)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.flags))
        
        data.write(Bytes(self.body))
        
        data.write(String(self.uri))
        
        data.write(String(self.queryParams))
        
        return data.getvalue()
