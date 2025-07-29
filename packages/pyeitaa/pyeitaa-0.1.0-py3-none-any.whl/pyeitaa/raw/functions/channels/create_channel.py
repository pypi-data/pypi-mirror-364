from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class CreateChannel(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3d5fb10f``

    Parameters:
        title: ``str``
        about: ``str``
        broadcast (optional): ``bool``
        megagroup (optional): ``bool``
        for_import (optional): ``bool``
        geo_point (optional): :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`
        address (optional): ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["title", "about", "broadcast", "megagroup", "for_import", "geo_point", "address"]

    ID = 0x3d5fb10f
    QUALNAME = "functions.channels.CreateChannel"

    def __init__(self, *, title: str, about: str, broadcast: Optional[bool] = None, megagroup: Optional[bool] = None, for_import: Optional[bool] = None, geo_point: "raw.base.InputGeoPoint" = None, address: Optional[str] = None) -> None:
        self.title = title  # string
        self.about = about  # string
        self.broadcast = broadcast  # flags.0?true
        self.megagroup = megagroup  # flags.1?true
        self.for_import = for_import  # flags.3?true
        self.geo_point = geo_point  # flags.2?InputGeoPoint
        self.address = address  # flags.2?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        broadcast = True if flags & (1 << 0) else False
        megagroup = True if flags & (1 << 1) else False
        for_import = True if flags & (1 << 3) else False
        title = String.read(data)
        
        about = String.read(data)
        
        geo_point = TLObject.read(data) if flags & (1 << 2) else None
        
        address = String.read(data) if flags & (1 << 2) else None
        return CreateChannel(title=title, about=about, broadcast=broadcast, megagroup=megagroup, for_import=for_import, geo_point=geo_point, address=address)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.broadcast else 0
        flags |= (1 << 1) if self.megagroup else 0
        flags |= (1 << 3) if self.for_import else 0
        flags |= (1 << 2) if self.geo_point is not None else 0
        flags |= (1 << 2) if self.address is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.title))
        
        data.write(String(self.about))
        
        if self.geo_point is not None:
            data.write(self.geo_point.write())
        
        if self.address is not None:
            data.write(String(self.address))
        
        return data.getvalue()
