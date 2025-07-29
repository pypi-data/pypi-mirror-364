from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class PollAnswerVoters(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PollAnswerVoters`.

    Details:
        - Layer: ``135``
        - ID: ``0x3b6ddad2``

    Parameters:
        option: ``bytes``
        voters: ``int`` ``32-bit``
        chosen (optional): ``bool``
        correct (optional): ``bool``
    """

    __slots__: List[str] = ["option", "voters", "chosen", "correct"]

    ID = 0x3b6ddad2
    QUALNAME = "types.PollAnswerVoters"

    def __init__(self, *, option: bytes, voters: int, chosen: Optional[bool] = None, correct: Optional[bool] = None) -> None:
        self.option = option  # bytes
        self.voters = voters  # int
        self.chosen = chosen  # flags.0?true
        self.correct = correct  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        chosen = True if flags & (1 << 0) else False
        correct = True if flags & (1 << 1) else False
        option = Bytes.read(data)
        
        voters = Int.read(data)
        
        return PollAnswerVoters(option=option, voters=voters, chosen=chosen, correct=correct)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.chosen else 0
        flags |= (1 << 1) if self.correct else 0
        data.write(Int(flags))
        
        data.write(Bytes(self.option))
        
        data.write(Int(self.voters))
        
        return data.getvalue()
