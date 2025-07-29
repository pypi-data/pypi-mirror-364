from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateBotInlineSend(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x12f12a07``

    Parameters:
        user_id: ``int`` ``64-bit``
        query: ``str``
        id: ``str``
        geo (optional): :obj:`GeoPoint <pyeitaa.raw.base.GeoPoint>`
        msg_id (optional): :obj:`InputBotInlineMessageID <pyeitaa.raw.base.InputBotInlineMessageID>`
    """

    __slots__: List[str] = ["user_id", "query", "id", "geo", "msg_id"]

    ID = 0x12f12a07
    QUALNAME = "types.UpdateBotInlineSend"

    def __init__(self, *, user_id: int, query: str, id: str, geo: "raw.base.GeoPoint" = None, msg_id: "raw.base.InputBotInlineMessageID" = None) -> None:
        self.user_id = user_id  # long
        self.query = query  # string
        self.id = id  # string
        self.geo = geo  # flags.0?GeoPoint
        self.msg_id = msg_id  # flags.1?InputBotInlineMessageID

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        user_id = Long.read(data)
        
        query = String.read(data)
        
        geo = TLObject.read(data) if flags & (1 << 0) else None
        
        id = String.read(data)
        
        msg_id = TLObject.read(data) if flags & (1 << 1) else None
        
        return UpdateBotInlineSend(user_id=user_id, query=query, id=id, geo=geo, msg_id=msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.geo is not None else 0
        flags |= (1 << 1) if self.msg_id is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.user_id))
        
        data.write(String(self.query))
        
        if self.geo is not None:
            data.write(self.geo.write())
        
        data.write(String(self.id))
        
        if self.msg_id is not None:
            data.write(self.msg_id.write())
        
        return data.getvalue()
