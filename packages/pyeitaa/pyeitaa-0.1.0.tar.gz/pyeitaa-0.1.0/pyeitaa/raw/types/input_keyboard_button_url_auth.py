from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputKeyboardButtonUrlAuth(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.KeyboardButton`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2fd1802c``

    Parameters:
        text: ``str``
        url: ``str``
        bot: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        request_write_access (optional): ``bool``
        fwd_text (optional): ``str``
    """

    __slots__: List[str] = ["text", "url", "bot", "request_write_access", "fwd_text"]

    ID = -0x2fd1802c
    QUALNAME = "types.InputKeyboardButtonUrlAuth"

    def __init__(self, *, text: str, url: str, bot: "raw.base.InputUser", request_write_access: Optional[bool] = None, fwd_text: Optional[str] = None) -> None:
        self.text = text  # string
        self.url = url  # string
        self.bot = bot  # InputUser
        self.request_write_access = request_write_access  # flags.0?true
        self.fwd_text = fwd_text  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        request_write_access = True if flags & (1 << 0) else False
        text = String.read(data)
        
        fwd_text = String.read(data) if flags & (1 << 1) else None
        url = String.read(data)
        
        bot = TLObject.read(data)
        
        return InputKeyboardButtonUrlAuth(text=text, url=url, bot=bot, request_write_access=request_write_access, fwd_text=fwd_text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.request_write_access else 0
        flags |= (1 << 1) if self.fwd_text is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.text))
        
        if self.fwd_text is not None:
            data.write(String(self.fwd_text))
        
        data.write(String(self.url))
        
        data.write(self.bot.write())
        
        return data.getvalue()
