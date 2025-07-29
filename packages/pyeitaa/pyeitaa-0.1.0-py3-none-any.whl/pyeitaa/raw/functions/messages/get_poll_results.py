from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetPollResults(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x73bb643b``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id: ``int`` ``32-bit``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "msg_id"]

    ID = 0x73bb643b
    QUALNAME = "functions.messages.GetPollResults"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        return GetPollResults(peer=peer, msg_id=msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        return data.getvalue()
