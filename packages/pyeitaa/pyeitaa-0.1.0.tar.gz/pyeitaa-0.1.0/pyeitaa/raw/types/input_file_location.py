from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputFileLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2025541f``

    Parameters:
        volume_id: ``int`` ``64-bit``
        local_id: ``int`` ``32-bit``
        secret: ``int`` ``64-bit``
        file_reference: ``bytes``
    """

    __slots__: List[str] = ["volume_id", "local_id", "secret", "file_reference"]

    ID = -0x2025541f
    QUALNAME = "types.InputFileLocation"

    def __init__(self, *, volume_id: int, local_id: int, secret: int, file_reference: bytes) -> None:
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int
        self.secret = secret  # long
        self.file_reference = file_reference  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        volume_id = Long.read(data)
        
        local_id = Int.read(data)
        
        secret = Long.read(data)
        
        file_reference = Bytes.read(data)
        
        return InputFileLocation(volume_id=volume_id, local_id=local_id, secret=secret, file_reference=file_reference)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.volume_id))
        
        data.write(Int(self.local_id))
        
        data.write(Long(self.secret))
        
        data.write(Bytes(self.file_reference))
        
        return data.getvalue()
