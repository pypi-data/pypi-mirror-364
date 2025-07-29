from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionGameScore(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6d58d78a``

    Parameters:
        game_id: ``int`` ``64-bit``
        score: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["game_id", "score"]

    ID = -0x6d58d78a
    QUALNAME = "types.MessageActionGameScore"

    def __init__(self, *, game_id: int, score: int) -> None:
        self.game_id = game_id  # long
        self.score = score  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        game_id = Long.read(data)
        
        score = Int.read(data)
        
        return MessageActionGameScore(game_id=game_id, score=score)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.game_id))
        
        data.write(Int(self.score))
        
        return data.getvalue()
