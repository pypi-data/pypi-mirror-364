from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UpdateChannelMessageForwards(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2d65d80c``

    Parameters:
        channel_id: ``int`` ``64-bit``
        id: ``int`` ``32-bit``
        forwards: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "id", "forwards"]

    ID = -0x2d65d80c
    QUALNAME = "types.UpdateChannelMessageForwards"

    def __init__(self, *, channel_id: int, id: int, forwards: int) -> None:
        self.channel_id = channel_id  # long
        self.id = id  # int
        self.forwards = forwards  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel_id = Long.read(data)
        
        id = Int.read(data)
        
        forwards = Int.read(data)
        
        return UpdateChannelMessageForwards(channel_id=channel_id, id=id, forwards=forwards)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.channel_id))
        
        data.write(Int(self.id))
        
        data.write(Int(self.forwards))
        
        return data.getvalue()
