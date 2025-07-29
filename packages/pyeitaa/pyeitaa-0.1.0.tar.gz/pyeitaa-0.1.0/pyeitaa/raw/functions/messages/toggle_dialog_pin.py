from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ToggleDialogPin(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x58ce1da9``

    Parameters:
        peer: :obj:`InputDialogPeer <pyeitaa.raw.base.InputDialogPeer>`
        pinned (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "pinned"]

    ID = -0x58ce1da9
    QUALNAME = "functions.messages.ToggleDialogPin"

    def __init__(self, *, peer: "raw.base.InputDialogPeer", pinned: Optional[bool] = None) -> None:
        self.peer = peer  # InputDialogPeer
        self.pinned = pinned  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        pinned = True if flags & (1 << 0) else False
        peer = TLObject.read(data)
        
        return ToggleDialogPin(peer=peer, pinned=pinned)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.pinned else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        return data.getvalue()
