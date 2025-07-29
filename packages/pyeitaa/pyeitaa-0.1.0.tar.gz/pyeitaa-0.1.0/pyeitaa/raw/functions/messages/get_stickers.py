from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetStickers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x2a5a2c5f``

    Parameters:
        emoticon: ``str``
        hash: ``int`` ``64-bit``

    Returns:
        :obj:`messages.Stickers <pyeitaa.raw.base.messages.Stickers>`
    """

    __slots__: List[str] = ["emoticon", "hash"]

    ID = -0x2a5a2c5f
    QUALNAME = "functions.messages.GetStickers"

    def __init__(self, *, emoticon: str, hash: int) -> None:
        self.emoticon = emoticon  # string
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        emoticon = String.read(data)
        
        hash = Long.read(data)
        
        return GetStickers(emoticon=emoticon, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.emoticon))
        
        data.write(Long(self.hash))
        
        return data.getvalue()
