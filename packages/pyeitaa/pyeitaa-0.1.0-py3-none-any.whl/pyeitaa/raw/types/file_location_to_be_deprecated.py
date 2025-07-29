from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class FileLocationToBeDeprecated(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.FileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x43803933``

    Parameters:
        volume_id: ``int`` ``64-bit``
        local_id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["volume_id", "local_id"]

    ID = -0x43803933
    QUALNAME = "types.FileLocationToBeDeprecated"

    def __init__(self, *, volume_id: int, local_id: int) -> None:
        self.volume_id = volume_id  # long
        self.local_id = local_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        volume_id = Long.read(data)
        
        local_id = Int.read(data)
        
        return FileLocationToBeDeprecated(volume_id=volume_id, local_id=local_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.volume_id))
        
        data.write(Int(self.local_id))
        
        return data.getvalue()
