from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputEncryptedFileLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0xadca2ab``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id", "access_hash"]

    ID = -0xadca2ab
    QUALNAME = "types.InputEncryptedFileLocation"

    def __init__(self, *, id: int, access_hash: int) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        return InputEncryptedFileLocation(id=id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
