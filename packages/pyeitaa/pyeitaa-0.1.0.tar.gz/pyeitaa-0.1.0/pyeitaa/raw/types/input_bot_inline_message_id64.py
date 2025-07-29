from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputBotInlineMessageID64(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineMessageID`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4926ea29``

    Parameters:
        dc_id: ``int`` ``32-bit``
        owner_id: ``int`` ``64-bit``
        id: ``int`` ``32-bit``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["dc_id", "owner_id", "id", "access_hash"]

    ID = -0x4926ea29
    QUALNAME = "types.InputBotInlineMessageID64"

    def __init__(self, *, dc_id: int, owner_id: int, id: int, access_hash: int) -> None:
        self.dc_id = dc_id  # int
        self.owner_id = owner_id  # long
        self.id = id  # int
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dc_id = Int.read(data)
        
        owner_id = Long.read(data)
        
        id = Int.read(data)
        
        access_hash = Long.read(data)
        
        return InputBotInlineMessageID64(dc_id=dc_id, owner_id=owner_id, id=id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.dc_id))
        
        data.write(Long(self.owner_id))
        
        data.write(Int(self.id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
