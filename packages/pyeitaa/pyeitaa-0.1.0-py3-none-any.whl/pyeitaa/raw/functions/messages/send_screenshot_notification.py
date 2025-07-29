from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendScreenshotNotification(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x36820fe0``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        reply_to_msg_id: ``int`` ``32-bit``
        random_id: ``int`` ``64-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "reply_to_msg_id", "random_id"]

    ID = -0x36820fe0
    QUALNAME = "functions.messages.SendScreenshotNotification"

    def __init__(self, *, peer: "raw.base.InputPeer", reply_to_msg_id: int, random_id: int) -> None:
        self.peer = peer  # InputPeer
        self.reply_to_msg_id = reply_to_msg_id  # int
        self.random_id = random_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        reply_to_msg_id = Int.read(data)
        
        random_id = Long.read(data)
        
        return SendScreenshotNotification(peer=peer, reply_to_msg_id=reply_to_msg_id, random_id=random_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.reply_to_msg_id))
        
        data.write(Long(self.random_id))
        
        return data.getvalue()
