from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputBotInlineResultGame(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineResult`.

    Details:
        - Layer: ``135``
        - ID: ``0x4fa417f2``

    Parameters:
        id: ``str``
        short_name: ``str``
        send_message: :obj:`InputBotInlineMessage <pyeitaa.raw.base.InputBotInlineMessage>`
    """

    __slots__: List[str] = ["id", "short_name", "send_message"]

    ID = 0x4fa417f2
    QUALNAME = "types.InputBotInlineResultGame"

    def __init__(self, *, id: str, short_name: str, send_message: "raw.base.InputBotInlineMessage") -> None:
        self.id = id  # string
        self.short_name = short_name  # string
        self.send_message = send_message  # InputBotInlineMessage

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = String.read(data)
        
        short_name = String.read(data)
        
        send_message = TLObject.read(data)
        
        return InputBotInlineResultGame(id=id, short_name=short_name, send_message=send_message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.id))
        
        data.write(String(self.short_name))
        
        data.write(self.send_message.write())
        
        return data.getvalue()
