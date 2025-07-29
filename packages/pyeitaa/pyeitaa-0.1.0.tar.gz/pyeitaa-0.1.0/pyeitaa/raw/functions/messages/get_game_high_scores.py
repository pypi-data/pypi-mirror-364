from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetGameHighScores(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x17dd9b63``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: ``int`` ``32-bit``
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`

    Returns:
        :obj:`messages.HighScores <pyeitaa.raw.base.messages.HighScores>`
    """

    __slots__: List[str] = ["peer", "id", "user_id"]

    ID = -0x17dd9b63
    QUALNAME = "functions.messages.GetGameHighScores"

    def __init__(self, *, peer: "raw.base.InputPeer", id: int, user_id: "raw.base.InputUser") -> None:
        self.peer = peer  # InputPeer
        self.id = id  # int
        self.user_id = user_id  # InputUser

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        id = Int.read(data)
        
        user_id = TLObject.read(data)
        
        return GetGameHighScores(peer=peer, id=id, user_id=user_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Int(self.id))
        
        data.write(self.user_id.write())
        
        return data.getvalue()
