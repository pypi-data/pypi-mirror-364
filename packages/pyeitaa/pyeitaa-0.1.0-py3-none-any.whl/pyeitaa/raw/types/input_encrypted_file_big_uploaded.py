from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputEncryptedFileBigUploaded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputEncryptedFile`.

    Details:
        - Layer: ``135``
        - ID: ``0x2dc173c8``

    Parameters:
        id: ``int`` ``64-bit``
        parts: ``int`` ``32-bit``
        key_fingerprint: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "parts", "key_fingerprint"]

    ID = 0x2dc173c8
    QUALNAME = "types.InputEncryptedFileBigUploaded"

    def __init__(self, *, id: int, parts: int, key_fingerprint: int) -> None:
        self.id = id  # long
        self.parts = parts  # int
        self.key_fingerprint = key_fingerprint  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        parts = Int.read(data)
        
        key_fingerprint = Int.read(data)
        
        return InputEncryptedFileBigUploaded(id=id, parts=parts, key_fingerprint=key_fingerprint)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Int(self.parts))
        
        data.write(Int(self.key_fingerprint))
        
        return data.getvalue()
