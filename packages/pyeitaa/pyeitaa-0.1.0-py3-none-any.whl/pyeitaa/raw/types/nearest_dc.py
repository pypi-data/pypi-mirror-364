from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class NearestDc(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.NearestDc`.

    Details:
        - Layer: ``135``
        - ID: ``-0x71e5e88b``

    Parameters:
        country: ``str``
        this_dc: ``int`` ``32-bit``
        nearest_dc: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetNearestDc <pyeitaa.raw.functions.help.GetNearestDc>`
    """

    __slots__: List[str] = ["country", "this_dc", "nearest_dc"]

    ID = -0x71e5e88b
    QUALNAME = "types.NearestDc"

    def __init__(self, *, country: str, this_dc: int, nearest_dc: int) -> None:
        self.country = country  # string
        self.this_dc = this_dc  # int
        self.nearest_dc = nearest_dc  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        country = String.read(data)
        
        this_dc = Int.read(data)
        
        nearest_dc = Int.read(data)
        
        return NearestDc(country=country, this_dc=this_dc, nearest_dc=nearest_dc)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.country))
        
        data.write(Int(self.this_dc))
        
        data.write(Int(self.nearest_dc))
        
        return data.getvalue()
