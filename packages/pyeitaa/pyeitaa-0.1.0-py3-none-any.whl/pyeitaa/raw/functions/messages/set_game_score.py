from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SetGameScore(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x71071340``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        id: ``int`` ``32-bit``
        user_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        score: ``int`` ``32-bit``
        edit_message (optional): ``bool``
        force (optional): ``bool``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "id", "user_id", "score", "edit_message", "force"]

    ID = -0x71071340
    QUALNAME = "functions.messages.SetGameScore"

    def __init__(self, *, peer: "raw.base.InputPeer", id: int, user_id: "raw.base.InputUser", score: int, edit_message: Optional[bool] = None, force: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.id = id  # int
        self.user_id = user_id  # InputUser
        self.score = score  # int
        self.edit_message = edit_message  # flags.0?true
        self.force = force  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        edit_message = True if flags & (1 << 0) else False
        force = True if flags & (1 << 1) else False
        peer = TLObject.read(data)
        
        id = Int.read(data)
        
        user_id = TLObject.read(data)
        
        score = Int.read(data)
        
        return SetGameScore(peer=peer, id=id, user_id=user_id, score=score, edit_message=edit_message, force=force)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.edit_message else 0
        flags |= (1 << 1) if self.force else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.id))
        
        data.write(self.user_id.write())
        
        data.write(Int(self.score))
        
        return data.getvalue()
