from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class MarkDialogUnread(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3d792671``

    Parameters:
        peer: :obj:`InputDialogPeer <pyeitaa.raw.base.InputDialogPeer>`
        unread (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "unread"]

    ID = -0x3d792671
    QUALNAME = "functions.messages.MarkDialogUnread"

    def __init__(self, *, peer: "raw.base.InputDialogPeer", unread: Optional[bool] = None) -> None:
        self.peer = peer  # InputDialogPeer
        self.unread = unread  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        unread = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        return MarkDialogUnread(peer=peer, unread=unread)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.unread else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        return data.getvalue()
