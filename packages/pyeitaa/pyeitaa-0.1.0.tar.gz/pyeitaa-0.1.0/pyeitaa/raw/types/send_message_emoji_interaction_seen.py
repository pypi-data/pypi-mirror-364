from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SendMessageEmojiInteractionSeen(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SendMessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x499a6fd2``

    Parameters:
        emoticon: ``str``
    """

    __slots__: List[str] = ["emoticon"]

    ID = -0x499a6fd2
    QUALNAME = "types.SendMessageEmojiInteractionSeen"

    def __init__(self, *, emoticon: str) -> None:
        self.emoticon = emoticon  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        emoticon = String.read(data)
        
        return SendMessageEmojiInteractionSeen(emoticon=emoticon)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.emoticon))
        
        return data.getvalue()
