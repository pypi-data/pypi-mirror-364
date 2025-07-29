from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateGeoLiveViewed(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x78e046c7``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        msg_id: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer", "msg_id"]

    ID = -0x78e046c7
    QUALNAME = "types.UpdateGeoLiveViewed"

    def __init__(self, *, peer: "raw.base.Peer", msg_id: int) -> None:
        self.peer = peer  # Peer
        self.msg_id = msg_id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        return UpdateGeoLiveViewed(peer=peer, msg_id=msg_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        return data.getvalue()
