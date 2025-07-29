from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class RecentMeUrlStickerSet(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RecentMeUrl`.

    Details:
        - Layer: ``135``
        - ID: ``-0x43f5a824``

    Parameters:
        url: ``str``
        set: :obj:`StickerSetCovered <pyeitaa.raw.base.StickerSetCovered>`
    """

    __slots__: List[str] = ["url", "set"]

    ID = -0x43f5a824
    QUALNAME = "types.RecentMeUrlStickerSet"

    def __init__(self, *, url: str, set: "raw.base.StickerSetCovered") -> None:
        self.url = url  # string
        self.set = set  # StickerSetCovered

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        set = TLObject.read(data)
        
        return RecentMeUrlStickerSet(url=url, set=set)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(self.set.write())
        
        return data.getvalue()
