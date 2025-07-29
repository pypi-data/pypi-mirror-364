from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class StickerSetInstallResultArchive(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.StickerSetInstallResult`.

    Details:
        - Layer: ``135``
        - ID: ``0x35e410a8``

    Parameters:
        sets: List of :obj:`StickerSetCovered <pyeitaa.raw.base.StickerSetCovered>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.InstallStickerSet <pyeitaa.raw.functions.messages.InstallStickerSet>`
    """

    __slots__: List[str] = ["sets"]

    ID = 0x35e410a8
    QUALNAME = "types.messages.StickerSetInstallResultArchive"

    def __init__(self, *, sets: List["raw.base.StickerSetCovered"]) -> None:
        self.sets = sets  # Vector<StickerSetCovered>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        sets = TLObject.read(data)
        
        return StickerSetInstallResultArchive(sets=sets)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.sets))
        
        return data.getvalue()
