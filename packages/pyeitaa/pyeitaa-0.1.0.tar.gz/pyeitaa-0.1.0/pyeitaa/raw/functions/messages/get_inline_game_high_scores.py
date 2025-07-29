from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetInlineGameHighScores(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0xf635e1b``

    Parameters:
        id: :obj:`InputBotInlineMessageID <pyeitaa.raw.base.InputBotInlineMessageID>`
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`messages.HighScores <pyeitaa.raw.base.messages.HighScores>`
    """

    __slots__: List[str] = ["id", "user_id"]

    ID = 0xf635e1b
    QUALNAME = "functions.messages.GetInlineGameHighScores"

    def __init__(self, *, id: "raw.base.InputBotInlineMessageID", user_id: "raw.base.InputUser") -> None:
        self.id = id  # InputBotInlineMessageID
        self.user_id = user_id  # InputUser

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        user_id = TLObject.read(data)
        
        return GetInlineGameHighScores(id=id, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        data.write(self.user_id.write())
        
        return data.getvalue()
