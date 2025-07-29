from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetMessagePublicForwards(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x5630281b``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        msg_id: ``int`` ``32-bit``
        offset_rate: ``int`` ``32-bit``
        offset_peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        offset_id: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``

    Returns:
        :obj:`messages.Messages <pyeitaa.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["channel", "msg_id", "offset_rate", "offset_peer", "offset_id", "limit"]

    ID = 0x5630281b
    QUALNAME = "functions.stats.GetMessagePublicForwards"

    def __init__(self, *, channel: "raw.base.InputChannel", msg_id: int, offset_rate: int, offset_peer: "raw.base.InputPeer", offset_id: int, limit: int) -> None:
        self.channel = channel  # InputChannel
        self.msg_id = msg_id  # int
        self.offset_rate = offset_rate  # int
        self.offset_peer = offset_peer  # InputPeer
        self.offset_id = offset_id  # int
        self.limit = limit  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        offset_rate = Int.read(data)
        
        offset_peer = TLObject.read(data)
        
        offset_id = Int.read(data)
        
        limit = Int.read(data)
        
        return GetMessagePublicForwards(channel=channel, msg_id=msg_id, offset_rate=offset_rate, offset_peer=offset_peer, offset_id=offset_id, limit=limit)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(Int(self.msg_id))
        
        data.write(Int(self.offset_rate))
        
        data.write(self.offset_peer.write())
        
        data.write(Int(self.offset_id))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
