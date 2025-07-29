from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputChannelFromMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputChannel`.

    Details:
        - Layer: ``135``
        - ID: ``0x5b934f9d``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id: ``int`` ``32-bit``
        channel_id: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["peer", "msg_id", "channel_id"]

    ID = 0x5b934f9d
    QUALNAME = "types.InputChannelFromMessage"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, channel_id: int) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.channel_id = channel_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        channel_id = Long.read(data)
        
        return InputChannelFromMessage(peer=peer, msg_id=msg_id, channel_id=channel_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        data.write(Long(self.channel_id))
        
        return data.getvalue()
