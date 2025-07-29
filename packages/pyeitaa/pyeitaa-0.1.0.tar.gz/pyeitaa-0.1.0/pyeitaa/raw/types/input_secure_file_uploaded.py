from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputSecureFileUploaded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputSecureFile`.

    Details:
        - Layer: ``135``
        - ID: ``0x3334b0f0``

    Parameters:
        id: ``int`` ``64-bit``
        parts: ``int`` ``32-bit``
        md5_checksum: ``str``
        file_hash: ``bytes``
        secret: ``bytes``
    """

    __slots__: List[str] = ["id", "parts", "md5_checksum", "file_hash", "secret"]

    ID = 0x3334b0f0
    QUALNAME = "types.InputSecureFileUploaded"

    def __init__(self, *, id: int, parts: int, md5_checksum: str, file_hash: bytes, secret: bytes) -> None:
        self.id = id  # long
        self.parts = parts  # int
        self.md5_checksum = md5_checksum  # string
        self.file_hash = file_hash  # bytes
        self.secret = secret  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        parts = Int.read(data)
        
        md5_checksum = String.read(data)
        
        file_hash = Bytes.read(data)
        
        secret = Bytes.read(data)
        
        return InputSecureFileUploaded(id=id, parts=parts, md5_checksum=md5_checksum, file_hash=file_hash, secret=secret)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Int(self.parts))
        
        data.write(String(self.md5_checksum))
        
        data.write(Bytes(self.file_hash))
        
        data.write(Bytes(self.secret))
        
        return data.getvalue()
