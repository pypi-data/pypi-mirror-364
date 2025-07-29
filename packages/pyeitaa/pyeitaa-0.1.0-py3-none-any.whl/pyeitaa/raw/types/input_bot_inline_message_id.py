from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputBotInlineMessageID(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineMessageID`.

    Details:
        - Layer: ``135``
        - ID: ``-0x76f3c277``

    Parameters:
        dc_id: ``int`` ``32-bit``
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["dc_id", "id", "access_hash"]

    ID = -0x76f3c277
    QUALNAME = "types.InputBotInlineMessageID"

    def __init__(self, *, dc_id: int, id: int, access_hash: int) -> None:
        self.dc_id = dc_id  # int
        self.id = id  # long
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dc_id = Int.read(data)
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        return InputBotInlineMessageID(dc_id=dc_id, id=id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.dc_id))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
