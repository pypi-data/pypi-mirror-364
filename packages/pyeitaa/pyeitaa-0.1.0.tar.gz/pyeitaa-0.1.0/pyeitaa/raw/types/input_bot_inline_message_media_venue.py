from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputBotInlineMessageMediaVenue(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputBotInlineMessage`.

    Details:
        - Layer: ``135``
        - ID: ``0x417bbf11``

    Parameters:
        geo_point: :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`
        title: ``str``
        address: ``str``
        provider: ``str``
        venue_id: ``str``
        venue_type: ``str``
        reply_markup (optional): :obj:`ReplyMarkup <pyeitaa.raw.base.ReplyMarkup>`
    """

    __slots__: List[str] = ["geo_point", "title", "address", "provider", "venue_id", "venue_type", "reply_markup"]

    ID = 0x417bbf11
    QUALNAME = "types.InputBotInlineMessageMediaVenue"

    def __init__(self, *, geo_point: "raw.base.InputGeoPoint", title: str, address: str, provider: str, venue_id: str, venue_type: str, reply_markup: "raw.base.ReplyMarkup" = None) -> None:
        self.geo_point = geo_point  # InputGeoPoint
        self.title = title  # string
        self.address = address  # string
        self.provider = provider  # string
        self.venue_id = venue_id  # string
        self.venue_type = venue_type  # string
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        geo_point = TLObject.read(data)
        
        title = String.read(data)
        
        address = String.read(data)
        
        provider = String.read(data)
        
        venue_id = String.read(data)
        
        venue_type = String.read(data)
        
        reply_markup = TLObject.read(data) if flags & (1 << 2) else None
        
        return InputBotInlineMessageMediaVenue(geo_point=geo_point, title=title, address=address, provider=provider, venue_id=venue_id, venue_type=venue_type, reply_markup=reply_markup)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        data.write(Int(flags))
        
        data.write(self.geo_point.write())
        
        data.write(String(self.title))
        
        data.write(String(self.address))
        
        data.write(String(self.provider))
        
        data.write(String(self.venue_id))
        
        data.write(String(self.venue_type))
        
        if self.reply_markup is not None:
            data.write(self.reply_markup.write())
        
        return data.getvalue()
