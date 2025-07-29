from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class KeyboardButtonUrlAuth(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.KeyboardButton`.

    Details:
        - Layer: ``135``
        - ID: ``0x10b78d29``

    Parameters:
        text: ``str``
        url: ``str``
        button_id: ``int`` ``32-bit``
        fwd_text (optional): ``str``
    """

    __slots__: List[str] = ["text", "url", "button_id", "fwd_text"]

    ID = 0x10b78d29
    QUALNAME = "types.KeyboardButtonUrlAuth"

    def __init__(self, *, text: str, url: str, button_id: int, fwd_text: Optional[str] = None) -> None:
        self.text = text  # string
        self.url = url  # string
        self.button_id = button_id  # int
        self.fwd_text = fwd_text  # flags.0?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        text = String.read(data)
        
        fwd_text = String.read(data) if flags & (1 << 0) else None
        url = String.read(data)
        
        button_id = Int.read(data)
        
        return KeyboardButtonUrlAuth(text=text, url=url, button_id=button_id, fwd_text=fwd_text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.fwd_text is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.text))
        
        if self.fwd_text is not None:
            data.write(String(self.fwd_text))
        
        data.write(String(self.url))
        
        data.write(Int(self.button_id))
        
        return data.getvalue()
