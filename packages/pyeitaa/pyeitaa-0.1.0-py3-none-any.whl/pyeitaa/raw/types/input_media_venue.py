from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputMediaVenue(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3ec2e3ef``

    Parameters:
        geo_point: :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`
        title: ``str``
        address: ``str``
        provider: ``str``
        venue_id: ``str``
        venue_type: ``str``
    """

    __slots__: List[str] = ["geo_point", "title", "address", "provider", "venue_id", "venue_type"]

    ID = -0x3ec2e3ef
    QUALNAME = "types.InputMediaVenue"

    def __init__(self, *, geo_point: "raw.base.InputGeoPoint", title: str, address: str, provider: str, venue_id: str, venue_type: str) -> None:
        self.geo_point = geo_point  # InputGeoPoint
        self.title = title  # string
        self.address = address  # string
        self.provider = provider  # string
        self.venue_id = venue_id  # string
        self.venue_type = venue_type  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        geo_point = TLObject.read(data)
        
        title = String.read(data)
        
        address = String.read(data)
        
        provider = String.read(data)
        
        venue_id = String.read(data)
        
        venue_type = String.read(data)
        
        return InputMediaVenue(geo_point=geo_point, title=title, address=address, provider=provider, venue_id=venue_id, venue_type=venue_type)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.geo_point.write())
        
        data.write(String(self.title))
        
        data.write(String(self.address))
        
        data.write(String(self.provider))
        
        data.write(String(self.venue_id))
        
        data.write(String(self.venue_type))
        
        return data.getvalue()
