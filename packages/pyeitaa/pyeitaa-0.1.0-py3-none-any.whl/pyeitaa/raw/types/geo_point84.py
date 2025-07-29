from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Double
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GeoPoint84(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.GeoPoint`.

    Details:
        - Layer: ``135``
        - ID: ``0x2049d70c``

    Parameters:
        long: ``float`` ``64-bit``
        lat: ``float`` ``64-bit``
    """

    __slots__: List[str] = ["long", "lat"]

    ID = 0x2049d70c
    QUALNAME = "types.GeoPoint84"

    def __init__(self, *, long: float, lat: float) -> None:
        self.long = long  # double
        self.lat = lat  # double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        long = Double.read(data)
        
        lat = Double.read(data)
        
        return GeoPoint84(long=long, lat=lat)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Double(self.long))
        
        data.write(Double(self.lat))
        
        return data.getvalue()
