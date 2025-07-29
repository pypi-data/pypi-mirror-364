from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelParticipant(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelParticipant`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3ff3f840``

    Parameters:
        user_id: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "date"]

    ID = -0x3ff3f840
    QUALNAME = "types.ChannelParticipant"

    def __init__(self, *, user_id: int, date: int) -> None:
        self.user_id = user_id  # long
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        date = Int.read(data)
        
        return ChannelParticipant(user_id=user_id, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.date))
        
        return data.getvalue()
