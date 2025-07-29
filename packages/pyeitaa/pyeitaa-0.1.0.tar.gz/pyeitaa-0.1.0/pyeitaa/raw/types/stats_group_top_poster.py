from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class StatsGroupTopPoster(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatsGroupTopPoster`.

    Details:
        - Layer: ``135``
        - ID: ``-0x62fb5065``

    Parameters:
        user_id: ``int`` ``64-bit``
        messages: ``int`` ``32-bit``
        avg_chars: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["user_id", "messages", "avg_chars"]

    ID = -0x62fb5065
    QUALNAME = "types.StatsGroupTopPoster"

    def __init__(self, *, user_id: int, messages: int, avg_chars: int) -> None:
        self.user_id = user_id  # long
        self.messages = messages  # int
        self.avg_chars = avg_chars  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        messages = Int.read(data)
        
        avg_chars = Int.read(data)
        
        return StatsGroupTopPoster(user_id=user_id, messages=messages, avg_chars=avg_chars)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.messages))
        
        data.write(Int(self.avg_chars))
        
        return data.getvalue()
