from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class HighScore(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.HighScore`.

    Details:
        - Layer: ``135``
        - ID: ``0x73a379eb``

    Parameters:
        pos: ``int`` ``32-bit``
        user_id: ``int`` ``64-bit``
        score: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["pos", "user_id", "score"]

    ID = 0x73a379eb
    QUALNAME = "types.HighScore"

    def __init__(self, *, pos: int, user_id: int, score: int) -> None:
        self.pos = pos  # int
        self.user_id = user_id  # long
        self.score = score  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pos = Int.read(data)
        
        user_id = Long.read(data)
        
        score = Int.read(data)
        
        return HighScore(pos=pos, user_id=user_id, score=score)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.pos))
        
        data.write(Long(self.user_id))
        
        data.write(Int(self.score))
        
        return data.getvalue()
