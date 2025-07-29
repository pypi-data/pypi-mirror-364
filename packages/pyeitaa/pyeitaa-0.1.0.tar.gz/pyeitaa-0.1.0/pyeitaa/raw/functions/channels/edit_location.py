from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditLocation(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x58e63f6d``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        geo_point: :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`
        address: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["channel", "geo_point", "address"]

    ID = 0x58e63f6d
    QUALNAME = "functions.channels.EditLocation"

    def __init__(self, *, channel: "raw.base.InputChannel", geo_point: "raw.base.InputGeoPoint", address: str) -> None:
        self.channel = channel  # InputChannel
        self.geo_point = geo_point  # InputGeoPoint
        self.address = address  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        geo_point = TLObject.read(data)
        
        address = String.read(data)
        
        return EditLocation(channel=channel, geo_point=geo_point, address=address)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.geo_point.write())
        
        data.write(String(self.address))
        
        return data.getvalue()
