from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateDialogUnreadMark(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1e9ba63d``

    Parameters:
        peer: :obj:`DialogPeer <pyeitaa.raw.base.DialogPeer>`
        unread (optional): ``bool``
    """

    __slots__: List[str] = ["peer", "unread"]

    ID = -0x1e9ba63d
    QUALNAME = "types.UpdateDialogUnreadMark"

    def __init__(self, *, peer: "raw.base.DialogPeer", unread: Optional[bool] = None) -> None:
        self.peer = peer  # DialogPeer
        self.unread = unread  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        unread = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        return UpdateDialogUnreadMark(peer=peer, unread=unread)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.unread else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        return data.getvalue()
