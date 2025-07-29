from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PageBlockMap(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PageBlock`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5bb0c10a``

    Parameters:
        geo: :obj:`GeoPoint <pyeitaa.raw.base.GeoPoint>`
        zoom: ``int`` ``32-bit``
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
        caption: :obj:`PageCaption <pyeitaa.raw.base.PageCaption>`
    """

    __slots__: List[str] = ["geo", "zoom", "w", "h", "caption"]

    ID = -0x5bb0c10a
    QUALNAME = "types.PageBlockMap"

    def __init__(self, *, geo: "raw.base.GeoPoint", zoom: int, w: int, h: int, caption: "raw.base.PageCaption") -> None:
        self.geo = geo  # GeoPoint
        self.zoom = zoom  # int
        self.w = w  # int
        self.h = h  # int
        self.caption = caption  # PageCaption

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        geo = TLObject.read(data)
        
        zoom = Int.read(data)
        
        w = Int.read(data)
        
        h = Int.read(data)
        
        caption = TLObject.read(data)
        
        return PageBlockMap(geo=geo, zoom=zoom, w=w, h=h, caption=caption)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.geo.write())
        
        data.write(Int(self.zoom))
        
        data.write(Int(self.w))
        
        data.write(Int(self.h))
        
        data.write(self.caption.write())
        
        return data.getvalue()
