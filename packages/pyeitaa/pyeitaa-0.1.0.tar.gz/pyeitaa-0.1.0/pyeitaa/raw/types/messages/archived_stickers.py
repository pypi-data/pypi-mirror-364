from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ArchivedStickers(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.ArchivedStickers`.

    Details:
        - Layer: ``135``
        - ID: ``0x4fcba9c8``

    Parameters:
        count: ``int`` ``32-bit``
        sets: List of :obj:`StickerSetCovered <pyeitaa.raw.base.StickerSetCovered>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetArchivedStickers <pyeitaa.raw.functions.messages.GetArchivedStickers>`
    """

    __slots__: List[str] = ["count", "sets"]

    ID = 0x4fcba9c8
    QUALNAME = "types.messages.ArchivedStickers"

    def __init__(self, *, count: int, sets: List["raw.base.StickerSetCovered"]) -> None:
        self.count = count  # int
        self.sets = sets  # Vector<StickerSetCovered>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        sets = TLObject.read(data)
        
        return ArchivedStickers(count=count, sets=sets)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.sets))
        
        return data.getvalue()
