from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class Poll(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Poll`.

    Details:
        - Layer: ``135``
        - ID: ``-0x791e7e9f``

    Parameters:
        id: ``int`` ``64-bit``
        question: ``str``
        answers: List of :obj:`PollAnswer <pyeitaa.raw.base.PollAnswer>`
        closed (optional): ``bool``
        public_voters (optional): ``bool``
        multiple_choice (optional): ``bool``
        quiz (optional): ``bool``
        close_period (optional): ``int`` ``32-bit``
        close_date (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "question", "answers", "closed", "public_voters", "multiple_choice", "quiz", "close_period", "close_date"]

    ID = -0x791e7e9f
    QUALNAME = "types.Poll"

    def __init__(self, *, id: int, question: str, answers: List["raw.base.PollAnswer"], closed: Optional[bool] = None, public_voters: Optional[bool] = None, multiple_choice: Optional[bool] = None, quiz: Optional[bool] = None, close_period: Optional[int] = None, close_date: Optional[int] = None) -> None:
        self.id = id  # long
        self.question = question  # string
        self.answers = answers  # Vector<PollAnswer>
        self.closed = closed  # flags.0?true
        self.public_voters = public_voters  # flags.1?true
        self.multiple_choice = multiple_choice  # flags.2?true
        self.quiz = quiz  # flags.3?true
        self.close_period = close_period  # flags.4?int
        self.close_date = close_date  # flags.5?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        
        id = Long.read(data)
        flags = Int.read(data)
        
        closed = True if flags & (1 << 0) else False
        public_voters = True if flags & (1 << 1) else False
        multiple_choice = True if flags & (1 << 2) else False
        quiz = True if flags & (1 << 3) else False
        question = String.read(data)
        
        answers = TLObject.read(data)
        
        close_period = Int.read(data) if flags & (1 << 4) else None
        close_date = Int.read(data) if flags & (1 << 5) else None
        return Poll(id=id, question=question, answers=answers, closed=closed, public_voters=public_voters, multiple_choice=multiple_choice, quiz=quiz, close_period=close_period, close_date=close_date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        
        data.write(Long(self.id))
        flags = 0
        flags |= (1 << 0) if self.closed else 0
        flags |= (1 << 1) if self.public_voters else 0
        flags |= (1 << 2) if self.multiple_choice else 0
        flags |= (1 << 3) if self.quiz else 0
        flags |= (1 << 4) if self.close_period is not None else 0
        flags |= (1 << 5) if self.close_date is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.question))
        
        data.write(Vector(self.answers))
        
        if self.close_period is not None:
            data.write(Int(self.close_period))
        
        if self.close_date is not None:
            data.write(Int(self.close_date))
        
        return data.getvalue()
