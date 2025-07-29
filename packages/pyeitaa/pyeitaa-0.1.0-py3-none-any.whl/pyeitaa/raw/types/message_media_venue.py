from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MessageMediaVenue(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x2ec0533f``

    Parameters:
        geo: :obj:`GeoPoint <pyeitaa.raw.base.GeoPoint>`
        title: ``str``
        address: ``str``
        provider: ``str``
        venue_id: ``str``
        venue_type: ``str``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["geo", "title", "address", "provider", "venue_id", "venue_type"]

    ID = 0x2ec0533f
    QUALNAME = "types.MessageMediaVenue"

    def __init__(self, *, geo: "raw.base.GeoPoint", title: str, address: str, provider: str, venue_id: str, venue_type: str) -> None:
        self.geo = geo  # GeoPoint
        self.title = title  # string
        self.address = address  # string
        self.provider = provider  # string
        self.venue_id = venue_id  # string
        self.venue_type = venue_type  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        geo = TLObject.read(data)
        
        title = String.read(data)
        
        address = String.read(data)
        
        provider = String.read(data)
        
        venue_id = String.read(data)
        
        venue_type = String.read(data)
        
        return MessageMediaVenue(geo=geo, title=title, address=address, provider=provider, venue_id=venue_id, venue_type=venue_type)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.geo.write())
        
        data.write(String(self.title))
        
        data.write(String(self.address))
        
        data.write(String(self.provider))
        
        data.write(String(self.venue_id))
        
        data.write(String(self.venue_type))
        
        return data.getvalue()
