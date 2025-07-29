from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class KeyboardButtonCallback(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.KeyboardButton`.

    Details:
        - Layer: ``135``
        - ID: ``0x35bbdb6b``

    Parameters:
        text: ``str``
        data: ``bytes``
        requires_password (optional): ``bool``
    """

    __slots__: List[str] = ["text", "data", "requires_password"]

    ID = 0x35bbdb6b
    QUALNAME = "types.KeyboardButtonCallback"

    def __init__(self, *, text: str, data: bytes, requires_password: Optional[bool] = None) -> None:
        self.text = text  # string
        self.data = data  # bytes
        self.requires_password = requires_password  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        requires_password = True if flags & (1 << 0) else False
        text = String.read(data)
        
        data = Bytes.read(data)
        
        return KeyboardButtonCallback(text=text, data=data, requires_password=requires_password)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.requires_password else 0
        data.write(Int(flags))
        
        data.write(String(self.text))
        
        data.write(Bytes(self.data))
        
        return data.getvalue()
