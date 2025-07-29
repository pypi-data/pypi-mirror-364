from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PhotoPathSize(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhotoSize`.

    Details:
        - Layer: ``135``
        - ID: ``-0x27deb2bf``

    Parameters:
        type: ``str``
        bytes: ``bytes``
    """

    __slots__: List[str] = ["type", "bytes"]

    ID = -0x27deb2bf
    QUALNAME = "types.PhotoPathSize"

    def __init__(self, *, type: str, bytes: bytes) -> None:
        self.type = type  # string
        self.bytes = bytes  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = String.read(data)
        
        bytes = Bytes.read(data)
        
        return PhotoPathSize(type=type, bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.type))
        
        data.write(Bytes(self.bytes))
        
        return data.getvalue()
