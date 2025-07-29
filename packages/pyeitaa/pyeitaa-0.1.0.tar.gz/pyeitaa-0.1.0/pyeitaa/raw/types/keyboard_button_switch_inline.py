from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class KeyboardButtonSwitchInline(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.KeyboardButton`.

    Details:
        - Layer: ``135``
        - ID: ``0x568a748``

    Parameters:
        text: ``str``
        query: ``str``
        same_peer (optional): ``bool``
    """

    __slots__: List[str] = ["text", "query", "same_peer"]

    ID = 0x568a748
    QUALNAME = "types.KeyboardButtonSwitchInline"

    def __init__(self, *, text: str, query: str, same_peer: Optional[bool] = None) -> None:
        self.text = text  # string
        self.query = query  # string
        self.same_peer = same_peer  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        same_peer = True if flags & (1 << 0) else False
        text = String.read(data)
        
        query = String.read(data)
        
        return KeyboardButtonSwitchInline(text=text, query=query, same_peer=same_peer)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.same_peer else 0
        data.write(Int(flags))
        
        data.write(String(self.text))
        
        data.write(String(self.query))
        
        return data.getvalue()
