from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Double
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class GeoPoint(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.GeoPoint`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4d5d099d``

    Parameters:
        long: ``float`` ``64-bit``
        lat: ``float`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        accuracy_radius (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["long", "lat", "access_hash", "accuracy_radius"]

    ID = -0x4d5d099d
    QUALNAME = "types.GeoPoint"

    def __init__(self, *, long: float, lat: float, access_hash: int, accuracy_radius: Optional[int] = None) -> None:
        self.long = long  # double
        self.lat = lat  # double
        self.access_hash = access_hash  # long
        self.accuracy_radius = accuracy_radius  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        long = Double.read(data)
        
        lat = Double.read(data)
        
        access_hash = Long.read(data)
        
        accuracy_radius = Int.read(data) if flags & (1 << 0) else None
        return GeoPoint(long=long, lat=lat, access_hash=access_hash, accuracy_radius=accuracy_radius)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.accuracy_radius is not None else 0
        data.write(Int(flags))
        
        data.write(Double(self.long))
        
        data.write(Double(self.lat))
        
        data.write(Long(self.access_hash))
        
        if self.accuracy_radius is not None:
            data.write(Int(self.accuracy_radius))
        
        return data.getvalue()
