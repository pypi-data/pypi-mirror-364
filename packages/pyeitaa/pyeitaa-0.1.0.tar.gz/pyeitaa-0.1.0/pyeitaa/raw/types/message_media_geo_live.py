from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MessageMediaGeoLive(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x46bf399a``

    Parameters:
        geo: :obj:`GeoPoint <pyeitaa.raw.base.GeoPoint>`
        period: ``int`` ``32-bit``
        heading (optional): ``int`` ``32-bit``
        proximity_notification_radius (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["geo", "period", "heading", "proximity_notification_radius"]

    ID = -0x46bf399a
    QUALNAME = "types.MessageMediaGeoLive"

    def __init__(self, *, geo: "raw.base.GeoPoint", period: int, heading: Optional[int] = None, proximity_notification_radius: Optional[int] = None) -> None:
        self.geo = geo  # GeoPoint
        self.period = period  # int
        self.heading = heading  # flags.0?int
        self.proximity_notification_radius = proximity_notification_radius  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        geo = TLObject.read(data)
        
        heading = Int.read(data) if flags & (1 << 0) else None
        period = Int.read(data)
        
        proximity_notification_radius = Int.read(data) if flags & (1 << 1) else None
        return MessageMediaGeoLive(geo=geo, period=period, heading=heading, proximity_notification_radius=proximity_notification_radius)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.heading is not None else 0
        flags |= (1 << 1) if self.proximity_notification_radius is not None else 0
        data.write(Int(flags))
        
        data.write(self.geo.write())
        
        if self.heading is not None:
            data.write(Int(self.heading))
        
        data.write(Int(self.period))
        
        if self.proximity_notification_radius is not None:
            data.write(Int(self.proximity_notification_radius))
        
        return data.getvalue()
