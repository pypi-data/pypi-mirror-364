from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class KeyboardButtonRequestPoll(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.KeyboardButton`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4438aea3``

    Parameters:
        text: ``str``
        quiz (optional): ``bool``
    """

    __slots__: List[str] = ["text", "quiz"]

    ID = -0x4438aea3
    QUALNAME = "types.KeyboardButtonRequestPoll"

    def __init__(self, *, text: str, quiz: Optional[bool] = None) -> None:
        self.text = text  # string
        self.quiz = quiz  # flags.0?Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        quiz = Bool.read(data) if flags & (1 << 0) else None
        text = String.read(data)
        
        return KeyboardButtonRequestPoll(text=text, quiz=quiz)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.quiz is not None else 0
        data.write(Int(flags))
        
        if self.quiz is not None:
            data.write(Bool(self.quiz))
        
        data.write(String(self.text))
        
        return data.getvalue()
