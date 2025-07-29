from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionSetChatTheme(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x55879cbb``

    Parameters:
        emoticon: ``str``
    """

    __slots__: List[str] = ["emoticon"]

    ID = -0x55879cbb
    QUALNAME = "types.MessageActionSetChatTheme"

    def __init__(self, *, emoticon: str) -> None:
        self.emoticon = emoticon  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        emoticon = String.read(data)
        
        return MessageActionSetChatTheme(emoticon=emoticon)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.emoticon))
        
        return data.getvalue()
