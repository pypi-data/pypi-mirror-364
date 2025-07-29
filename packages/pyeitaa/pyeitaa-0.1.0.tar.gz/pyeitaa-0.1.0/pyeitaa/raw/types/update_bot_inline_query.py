from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateBotInlineQuery(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x496f379c``

    Parameters:
        query_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        query: ``str``
        offset: ``str``
        geo (optional): :obj:`GeoPoint <pyeitaa.raw.base.GeoPoint>`
        peer_type (optional): :obj:`InlineQueryPeerType <pyeitaa.raw.base.InlineQueryPeerType>`
    """

    __slots__: List[str] = ["query_id", "user_id", "query", "offset", "geo", "peer_type"]

    ID = 0x496f379c
    QUALNAME = "types.UpdateBotInlineQuery"

    def __init__(self, *, query_id: int, user_id: int, query: str, offset: str, geo: "raw.base.GeoPoint" = None, peer_type: "raw.base.InlineQueryPeerType" = None) -> None:
        self.query_id = query_id  # long
        self.user_id = user_id  # long
        self.query = query  # string
        self.offset = offset  # string
        self.geo = geo  # flags.0?GeoPoint
        self.peer_type = peer_type  # flags.1?InlineQueryPeerType

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        query_id = Long.read(data)
        
        user_id = Long.read(data)
        
        query = String.read(data)
        
        geo = TLObject.read(data) if flags & (1 << 0) else None
        
        peer_type = TLObject.read(data) if flags & (1 << 1) else None
        
        offset = String.read(data)
        
        return UpdateBotInlineQuery(query_id=query_id, user_id=user_id, query=query, offset=offset, geo=geo, peer_type=peer_type)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.geo is not None else 0
        flags |= (1 << 1) if self.peer_type is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        data.write(Long(self.user_id))
        
        data.write(String(self.query))
        
        if self.geo is not None:
            data.write(self.geo.write())
        
        if self.peer_type is not None:
            data.write(self.peer_type.write())
        
        data.write(String(self.offset))
        
        return data.getvalue()
