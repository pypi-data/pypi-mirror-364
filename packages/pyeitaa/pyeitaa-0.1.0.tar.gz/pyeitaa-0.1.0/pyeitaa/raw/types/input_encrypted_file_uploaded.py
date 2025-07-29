from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputEncryptedFileUploaded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputEncryptedFile`.

    Details:
        - Layer: ``135``
        - ID: ``0x64bd0306``

    Parameters:
        id: ``int`` ``64-bit``
        parts: ``int`` ``32-bit``
        md5_checksum: ``str``
        key_fingerprint: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "parts", "md5_checksum", "key_fingerprint"]

    ID = 0x64bd0306
    QUALNAME = "types.InputEncryptedFileUploaded"

    def __init__(self, *, id: int, parts: int, md5_checksum: str, key_fingerprint: int) -> None:
        self.id = id  # long
        self.parts = parts  # int
        self.md5_checksum = md5_checksum  # string
        self.key_fingerprint = key_fingerprint  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        parts = Int.read(data)
        
        md5_checksum = String.read(data)
        
        key_fingerprint = Int.read(data)
        
        return InputEncryptedFileUploaded(id=id, parts=parts, md5_checksum=md5_checksum, key_fingerprint=key_fingerprint)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Int(self.parts))
        
        data.write(String(self.md5_checksum))
        
        data.write(Int(self.key_fingerprint))
        
        return data.getvalue()
