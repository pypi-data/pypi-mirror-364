from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetInlineBotResults(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x514e999d``

    Parameters:
        bot: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        query: ``str``
        offset: ``str``
        geo_point (optional): :obj:`InputGeoPoint <pyeitaa.raw.base.InputGeoPoint>`

    Returns:
        :obj:`messages.BotResults <pyeitaa.raw.base.messages.BotResults>`
    """

    __slots__: List[str] = ["bot", "peer", "query", "offset", "geo_point"]

    ID = 0x514e999d
    QUALNAME = "functions.messages.GetInlineBotResults"

    def __init__(self, *, bot: "raw.base.InputUser", peer: "raw.base.InputPeer", query: str, offset: str, geo_point: "raw.base.InputGeoPoint" = None) -> None:
        self.bot = bot  # InputUser
        self.peer = peer  # InputPeer
        self.query = query  # string
        self.offset = offset  # string
        self.geo_point = geo_point  # flags.0?InputGeoPoint

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        bot = TLObject.read(data)
        
        peer = TLObject.read(data)
        
        geo_point = TLObject.read(data) if flags & (1 << 0) else None
        
        query = String.read(data)
        
        offset = String.read(data)
        
        return GetInlineBotResults(bot=bot, peer=peer, query=query, offset=offset, geo_point=geo_point)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.geo_point is not None else 0
        data.write(Int(flags))
        
        data.write(self.bot.write())
        
        data.write(self.peer.write())
        
        if self.geo_point is not None:
            data.write(self.geo_point.write())
        
        data.write(String(self.query))
        
        data.write(String(self.offset))
        
        return data.getvalue()
