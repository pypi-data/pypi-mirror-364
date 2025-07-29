from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Double
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MaskCoords(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MaskCoords`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5129244e``

    Parameters:
        n: ``int`` ``32-bit``
        x: ``float`` ``64-bit``
        y: ``float`` ``64-bit``
        zoom: ``float`` ``64-bit``
    """

    __slots__: List[str] = ["n", "x", "y", "zoom"]

    ID = -0x5129244e
    QUALNAME = "types.MaskCoords"

    def __init__(self, *, n: int, x: float, y: float, zoom: float) -> None:
        self.n = n  # int
        self.x = x  # double
        self.y = y  # double
        self.zoom = zoom  # double

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        n = Int.read(data)
        
        x = Double.read(data)
        
        y = Double.read(data)
        
        zoom = Double.read(data)
        
        return MaskCoords(n=n, x=x, y=y, zoom=zoom)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.n))
        
        data.write(Double(self.x))
        
        data.write(Double(self.y))
        
        data.write(Double(self.zoom))
        
        return data.getvalue()
