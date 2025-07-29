from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class FeaturedStickersNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.FeaturedStickers`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3923f39a``

    Parameters:
        count: ``int`` ``32-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetFeaturedStickers <pyeitaa.raw.functions.messages.GetFeaturedStickers>`
            - :obj:`messages.GetOldFeaturedStickers <pyeitaa.raw.functions.messages.GetOldFeaturedStickers>`
    """

    __slots__: List[str] = ["count"]

    ID = -0x3923f39a
    QUALNAME = "types.messages.FeaturedStickersNotModified"

    def __init__(self, *, count: int) -> None:
        self.count = count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        return FeaturedStickersNotModified(count=count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        return data.getvalue()
