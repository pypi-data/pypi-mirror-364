from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputPhotoLegacyFileLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x27cb990d``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        file_reference: ``bytes``
        volume_id: ``int`` ``64-bit``
        local_id: ``int`` ``32-bit``
        secret: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id", "access_hash", "file_reference", "volume_id", "local_id", "secret"]

    ID = -0x27cb990d
    QUALNAME = "types.InputPhotoLegacyFileLocation"

    def __init__(self, *, id: int, access_hash: int, file_reference: bytes, volume_id: int, local_id: int, secret: int) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.file_reference = file_reference  # bytes
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int
        self.secret = secret  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        file_reference = Bytes.read(data)
        
        volume_id = Long.read(data)
        
        local_id = Int.read(data)
        
        secret = Long.read(data)
        
        return InputPhotoLegacyFileLocation(id=id, access_hash=access_hash, file_reference=file_reference, volume_id=volume_id, local_id=local_id, secret=secret)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Bytes(self.file_reference))
        
        data.write(Long(self.volume_id))
        
        data.write(Int(self.local_id))
        
        data.write(Long(self.secret))
        
        return data.getvalue()
