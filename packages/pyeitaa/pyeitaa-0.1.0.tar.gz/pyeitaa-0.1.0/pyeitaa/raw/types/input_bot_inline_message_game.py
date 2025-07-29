from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputBotInlineMessageGame(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineMessage`.

    Details:
        - Layer: ``135``
        - ID: ``0x4b425864``

    Parameters:
        reply_markup (optional): :obj:`ReplyMarkup <pyeitaa.raw.base.ReplyMarkup>`
    """

    __slots__: List[str] = ["reply_markup"]

    ID = 0x4b425864
    QUALNAME = "types.InputBotInlineMessageGame"

    def __init__(self, *, reply_markup: "raw.base.ReplyMarkup" = None) -> None:
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        reply_markup = TLObject.read(data) if flags & (1 << 2) else None
        
        return InputBotInlineMessageGame(reply_markup=reply_markup)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        data.write(Int(flags))
        
        if self.reply_markup is not None:
            data.write(self.reply_markup.write())
        
        return data.getvalue()
