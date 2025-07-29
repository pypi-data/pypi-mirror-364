from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AdsGetAdsPack(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x38ab0d26``

    Parameters:
        flags: ``int`` ``32-bit``
        location: :obj:`AdsLocation <pyeitaa.raw.base.AdsLocation>`

    Returns:
        :obj:`AdsGetAdsPack <pyeitaa.raw.base.AdsGetAdsPack>`
    """

    __slots__: List[str] = ["flags", "location"]

    ID = 0x38ab0d26
    QUALNAME = "functions.AdsGetAdsPack"

    def __init__(self, *, flags: int, location: "raw.base.AdsLocation") -> None:
        self.flags = flags  # int
        self.location = location  # AdsLocation

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        flags = Int.read(data)
        
        location = TLObject.read(data)
        
        return AdsGetAdsPack(flags=flags, location=location)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.flags))
        
        data.write(self.location.write())
        
        return data.getvalue()
