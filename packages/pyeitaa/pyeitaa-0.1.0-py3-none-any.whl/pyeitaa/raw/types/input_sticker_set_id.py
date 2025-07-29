from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputStickerSetID(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputStickerSet`.

    Details:
        - Layer: ``135``
        - ID: ``-0x62185d97``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["id", "access_hash"]

    ID = -0x62185d97
    QUALNAME = "types.InputStickerSetID"

    def __init__(self, *, id: int, access_hash: int) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        return InputStickerSetID(id=id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
