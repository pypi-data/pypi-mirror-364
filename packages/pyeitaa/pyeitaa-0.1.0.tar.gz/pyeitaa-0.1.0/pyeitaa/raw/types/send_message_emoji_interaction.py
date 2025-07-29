from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendMessageEmojiInteraction(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SendMessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x6a3233b6``

    Parameters:
        emoticon: ``str``
        interaction: :obj:`DataJSON <pyeitaa.raw.base.DataJSON>`
    """

    __slots__: List[str] = ["emoticon", "interaction"]

    ID = 0x6a3233b6
    QUALNAME = "types.SendMessageEmojiInteraction"

    def __init__(self, *, emoticon: str, interaction: "raw.base.DataJSON") -> None:
        self.emoticon = emoticon  # string
        self.interaction = interaction  # DataJSON

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        emoticon = String.read(data)
        
        interaction = TLObject.read(data)
        
        return SendMessageEmojiInteraction(emoticon=emoticon, interaction=interaction)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.emoticon))
        
        data.write(self.interaction.write())
        
        return data.getvalue()
