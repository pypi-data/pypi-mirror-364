from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class DeleteHistory(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1c015b09``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        max_id: ``int`` ``32-bit``
        just_clear (optional): ``bool``
        revoke (optional): ``bool``

    Returns:
        :obj:`messages.AffectedHistory <pyeitaa.raw.base.messages.AffectedHistory>`
    """

    __slots__: List[str] = ["peer", "max_id", "just_clear", "revoke"]

    ID = 0x1c015b09
    QUALNAME = "functions.messages.DeleteHistory"

    def __init__(self, *, peer: "raw.base.InputPeer", max_id: int, just_clear: Optional[bool] = None, revoke: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.max_id = max_id  # int
        self.just_clear = just_clear  # flags.0?true
        self.revoke = revoke  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        just_clear = True if flags & (1 << 0) else False
        revoke = True if flags & (1 << 1) else False
        peer = TLObject.read(data)
        
        max_id = Int.read(data)
        
        return DeleteHistory(peer=peer, max_id=max_id, just_clear=just_clear, revoke=revoke)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.just_clear else 0
        flags |= (1 << 1) if self.revoke else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.max_id))
        
        return data.getvalue()
