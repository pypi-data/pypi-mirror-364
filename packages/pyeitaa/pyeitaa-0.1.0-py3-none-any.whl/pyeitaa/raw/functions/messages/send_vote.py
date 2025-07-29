from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SendVote(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x10ea6184``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id: ``int`` ``32-bit``
        options: List of ``bytes``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "msg_id", "options"]

    ID = 0x10ea6184
    QUALNAME = "functions.messages.SendVote"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, options: List[bytes]) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.options = options  # Vector<bytes>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        options = TLObject.read(data, Bytes)
        
        return SendVote(peer=peer, msg_id=msg_id, options=options)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        data.write(Vector(self.options, Bytes))
        
        return data.getvalue()
