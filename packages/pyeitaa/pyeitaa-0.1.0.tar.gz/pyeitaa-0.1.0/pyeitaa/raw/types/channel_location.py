from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelLocation`.

    Details:
        - Layer: ``135``
        - ID: ``0x209b82db``

    Parameters:
        geo_point: :obj:`GeoPoint <pyeitaa.raw.base.GeoPoint>`
        address: ``str``
    """

    __slots__: List[str] = ["geo_point", "address"]

    ID = 0x209b82db
    QUALNAME = "types.ChannelLocation"

    def __init__(self, *, geo_point: "raw.base.GeoPoint", address: str) -> None:
        self.geo_point = geo_point  # GeoPoint
        self.address = address  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        geo_point = TLObject.read(data)
        
        address = String.read(data)
        
        return ChannelLocation(geo_point=geo_point, address=address)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.geo_point.write())
        
        data.write(String(self.address))
        
        return data.getvalue()
