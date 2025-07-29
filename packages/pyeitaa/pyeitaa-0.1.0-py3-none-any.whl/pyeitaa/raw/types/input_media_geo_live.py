from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class InputMediaGeoLive(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x68e057bd``

    Parameters:
        geo_point: :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`
        stopped (optional): ``bool``
        heading (optional): ``int`` ``32-bit``
        period (optional): ``int`` ``32-bit``
        proximity_notification_radius (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["geo_point", "stopped", "heading", "period", "proximity_notification_radius"]

    ID = -0x68e057bd
    QUALNAME = "types.InputMediaGeoLive"

    def __init__(self, *, geo_point: "raw.base.InputGeoPoint", stopped: Optional[bool] = None, heading: Optional[int] = None, period: Optional[int] = None, proximity_notification_radius: Optional[int] = None) -> None:
        self.geo_point = geo_point  # InputGeoPoint
        self.stopped = stopped  # flags.0?true
        self.heading = heading  # flags.2?int
        self.period = period  # flags.1?int
        self.proximity_notification_radius = proximity_notification_radius  # flags.3?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        stopped = True if flags & (1 << 0) else False
        geo_point = TLObject.read(data)
        
        heading = Int.read(data) if flags & (1 << 2) else None
        period = Int.read(data) if flags & (1 << 1) else None
        proximity_notification_radius = Int.read(data) if flags & (1 << 3) else None
        return InputMediaGeoLive(geo_point=geo_point, stopped=stopped, heading=heading, period=period, proximity_notification_radius=proximity_notification_radius)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.stopped else 0
        flags |= (1 << 2) if self.heading is not None else 0
        flags |= (1 << 1) if self.period is not None else 0
        flags |= (1 << 3) if self.proximity_notification_radius is not None else 0
        data.write(Int(flags))
        
        data.write(self.geo_point.write())
        
        if self.heading is not None:
            data.write(Int(self.heading))
        
        if self.period is not None:
            data.write(Int(self.period))
        
        if self.proximity_notification_radius is not None:
            data.write(Int(self.proximity_notification_radius))
        
        return data.getvalue()
