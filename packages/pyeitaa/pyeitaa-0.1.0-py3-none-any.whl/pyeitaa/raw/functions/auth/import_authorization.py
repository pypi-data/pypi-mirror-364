from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ImportAuthorization(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5a858253``

    Parameters:
        id: ``int`` ``64-bit``
        bytes: ``bytes``

    Returns:
        :obj:`auth.Authorization <pyeitaa.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["id", "bytes"]

    ID = -0x5a858253
    QUALNAME = "functions.auth.ImportAuthorization"

    def __init__(self, *, id: int, bytes: bytes) -> None:
        self.id = id  # long
        self.bytes = bytes  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        bytes = Bytes.read(data)
        
        return ImportAuthorization(id=id, bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Bytes(self.bytes))
        
        return data.getvalue()
