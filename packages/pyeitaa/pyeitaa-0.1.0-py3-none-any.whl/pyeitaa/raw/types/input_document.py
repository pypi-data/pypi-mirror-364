from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputDocument(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputDocument`.

    Details:
        - Layer: ``135``
        - ID: ``0x1abfb575``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        file_reference: ``bytes``
    """

    __slots__: List[str] = ["id", "access_hash", "file_reference"]

    ID = 0x1abfb575
    QUALNAME = "types.InputDocument"

    def __init__(self, *, id: int, access_hash: int, file_reference: bytes) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.file_reference = file_reference  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        file_reference = Bytes.read(data)
        
        return InputDocument(id=id, access_hash=access_hash, file_reference=file_reference)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Bytes(self.file_reference))
        
        return data.getvalue()
