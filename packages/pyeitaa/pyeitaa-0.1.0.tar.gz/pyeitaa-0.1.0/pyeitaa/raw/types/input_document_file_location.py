from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputDocumentFileLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x452f8a7c``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        file_reference: ``bytes``
        thumb_size: ``str``
    """

    __slots__: List[str] = ["id", "access_hash", "file_reference", "thumb_size"]

    ID = -0x452f8a7c
    QUALNAME = "types.InputDocumentFileLocation"

    def __init__(self, *, id: int, access_hash: int, file_reference: bytes, thumb_size: str) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.file_reference = file_reference  # bytes
        self.thumb_size = thumb_size  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        file_reference = Bytes.read(data)
        
        thumb_size = String.read(data)
        
        return InputDocumentFileLocation(id=id, access_hash=access_hash, file_reference=file_reference, thumb_size=thumb_size)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Bytes(self.file_reference))
        
        data.write(String(self.thumb_size))
        
        return data.getvalue()
