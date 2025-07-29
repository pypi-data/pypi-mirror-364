from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AllStickers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.AllStickers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x32443145``

    Parameters:
        hash: ``int`` ``64-bit``
        sets: List of :obj:`StickerSet <pyeitaa.raw.base.StickerSet>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAllStickers <pyeitaa.raw.functions.messages.GetAllStickers>`
            - :obj:`messages.GetMaskStickers <pyeitaa.raw.functions.messages.GetMaskStickers>`
    """

    __slots__: List[str] = ["hash", "sets"]

    ID = -0x32443145
    QUALNAME = "types.messages.AllStickers"

    def __init__(self, *, hash: int, sets: List["raw.base.StickerSet"]) -> None:
        self.hash = hash  # long
        self.sets = sets  # Vector<StickerSet>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        hash = Long.read(data)
        
        sets = TLObject.read(data)
        
        return AllStickers(hash=hash, sets=sets)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.hash))
        
        data.write(Vector(self.sets))
        
        return data.getvalue()
