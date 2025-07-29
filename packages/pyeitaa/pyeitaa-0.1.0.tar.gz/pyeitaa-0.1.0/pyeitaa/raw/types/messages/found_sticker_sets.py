from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class FoundStickerSets(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.FoundStickerSets`.

    Details:
        - Layer: ``135``
        - ID: ``-0x750f622e``

    Parameters:
        hash: ``int`` ``64-bit``
        sets: List of :obj:`StickerSetCovered <pyeitaa.raw.base.StickerSetCovered>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.SearchStickerSets <pyeitaa.raw.functions.messages.SearchStickerSets>`
    """

    __slots__: List[str] = ["hash", "sets"]

    ID = -0x750f622e
    QUALNAME = "types.messages.FoundStickerSets"

    def __init__(self, *, hash: int, sets: List["raw.base.StickerSetCovered"]) -> None:
        self.hash = hash  # long
        self.sets = sets  # Vector<StickerSetCovered>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        sets = TLObject.read(data)
        
        return FoundStickerSets(hash=hash, sets=sets)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Vector(self.sets))
        
        return data.getvalue()
