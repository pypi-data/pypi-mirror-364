from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class FileLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.FileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``0x53d69076``

    Parameters:
        dc_id: ``int`` ``32-bit``
        volume_id: ``int`` ``64-bit``
        local_id: ``int`` ``32-bit``
        secret: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["dc_id", "volume_id", "local_id", "secret"]

    ID = 0x53d69076
    QUALNAME = "types.FileLocation"

    def __init__(self, *, dc_id: int, volume_id: int, local_id: int, secret: int) -> None:
        self.dc_id = dc_id  # int
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int
        self.secret = secret  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dc_id = Int.read(data)
        
        volume_id = Long.read(data)
        
        local_id = Int.read(data)
        
        secret = Long.read(data)
        
        return FileLocation(dc_id=dc_id, volume_id=volume_id, local_id=local_id, secret=secret)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.dc_id))
        
        data.write(Long(self.volume_id))
        
        data.write(Int(self.local_id))
        
        data.write(Long(self.secret))
        
        return data.getvalue()
