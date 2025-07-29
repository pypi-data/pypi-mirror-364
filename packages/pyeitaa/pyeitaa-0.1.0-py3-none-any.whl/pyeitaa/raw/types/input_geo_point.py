from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Double
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class InputGeoPoint(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputGeoPoint`.

    Details:
        - Layer: ``135``
        - ID: ``0x48222faf``

    Parameters:
        lat: ``float`` ``64-bit``
        long: ``float`` ``64-bit``
        accuracy_radius (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["lat", "long", "accuracy_radius"]

    ID = 0x48222faf
    QUALNAME = "types.InputGeoPoint"

    def __init__(self, *, lat: float, long: float, accuracy_radius: Optional[int] = None) -> None:
        self.lat = lat  # double
        self.long = long  # double
        self.accuracy_radius = accuracy_radius  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        lat = Double.read(data)
        
        long = Double.read(data)
        
        accuracy_radius = Int.read(data) if flags & (1 << 0) else None
        return InputGeoPoint(lat=lat, long=long, accuracy_radius=accuracy_radius)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.accuracy_radius is not None else 0
        data.write(Int(flags))
        
        data.write(Double(self.lat))
        
        data.write(Double(self.long))
        
        if self.accuracy_radius is not None:
            data.write(Int(self.accuracy_radius))
        
        return data.getvalue()
