from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class StatAd(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.StatAd`.

    Details:
        - Layer: ``135``
        - ID: ``-0x60f44110``

    Parameters:
        id: ``int`` ``32-bit``
        adsLocation: :obj:`AdsLocation <pyeitaa.raw.base.AdsLocation>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`StatAd <pyeitaa.raw.functions.StatAd>`
    """

    __slots__: List[str] = ["id", "adsLocation"]

    ID = -0x60f44110
    QUALNAME = "types.StatAd"

    def __init__(self, *, id: int, adsLocation: "raw.base.AdsLocation") -> None:
        self.id = id  # int
        self.adsLocation = adsLocation  # AdsLocation

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Int.read(data)
        
        adsLocation = TLObject.read(data)
        
        return StatAd(id=id, adsLocation=adsLocation)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.id))
        
        data.write(self.adsLocation.write())
        
        return data.getvalue()
