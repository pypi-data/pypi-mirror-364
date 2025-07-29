from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Stickers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.Stickers`.

    Details:
        - Layer: ``135``
        - ID: ``0x30a6ec7e``

    Parameters:
        hash: ``int`` ``64-bit``
        stickers: List of :obj:`Document <pyeitaa.raw.base.Document>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetStickers <pyeitaa.raw.functions.messages.GetStickers>`
    """

    __slots__: List[str] = ["hash", "stickers"]

    ID = 0x30a6ec7e
    QUALNAME = "types.messages.Stickers"

    def __init__(self, *, hash: int, stickers: List["raw.base.Document"]) -> None:
        self.hash = hash  # long
        self.stickers = stickers  # Vector<Document>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        stickers = TLObject.read(data)
        
        return Stickers(hash=hash, stickers=stickers)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Vector(self.stickers))
        
        return data.getvalue()
