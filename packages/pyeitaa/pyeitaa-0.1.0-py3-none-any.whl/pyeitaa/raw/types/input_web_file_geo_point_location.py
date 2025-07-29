from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputWebFileGeoPointLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputWebFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x60ddde37``

    Parameters:
        geo_point: :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`
        access_hash: ``int`` ``64-bit``
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
        zoom: ``int`` ``32-bit``
        scale: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["geo_point", "access_hash", "w", "h", "zoom", "scale"]

    ID = -0x60ddde37
    QUALNAME = "types.InputWebFileGeoPointLocation"

    def __init__(self, *, geo_point: "raw.base.InputGeoPoint", access_hash: int, w: int, h: int, zoom: int, scale: int) -> None:
        self.geo_point = geo_point  # InputGeoPoint
        self.access_hash = access_hash  # long
        self.w = w  # int
        self.h = h  # int
        self.zoom = zoom  # int
        self.scale = scale  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        geo_point = TLObject.read(data)
        
        access_hash = Long.read(data)
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        zoom = Int.read(data)
        
        scale = Int.read(data)
        
        return InputWebFileGeoPointLocation(geo_point=geo_point, access_hash=access_hash, w=w, h=h, zoom=zoom, scale=scale)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.geo_point.write())
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        data.write(Int(self.zoom))
        
        data.write(Int(self.scale))
        
        return data.getvalue()
