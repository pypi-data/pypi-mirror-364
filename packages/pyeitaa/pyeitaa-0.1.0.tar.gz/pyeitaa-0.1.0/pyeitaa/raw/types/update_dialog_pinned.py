from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateDialogPinned(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x6e6fe51c``

    Parameters:
        peer: :obj:`DialogPeer <pyeitaa.raw.base.DialogPeer>`
        pinned (optional): ``bool``
        folder_id (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["peer", "pinned", "folder_id"]

    ID = 0x6e6fe51c
    QUALNAME = "types.UpdateDialogPinned"

    def __init__(self, *, peer: "raw.base.DialogPeer", pinned: Optional[bool] = None, folder_id: Optional[int] = None) -> None:
        self.peer = peer  # DialogPeer
        self.pinned = pinned  # flags.0?true
        self.folder_id = folder_id  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        pinned = True if flags & (1 << 0) else False
        folder_id = Int.read(data) if flags & (1 << 1) else None
        peer = TLObject.read(data)
        
        return UpdateDialogPinned(peer=peer, pinned=pinned, folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.pinned else 0
        flags |= (1 << 1) if self.folder_id is not None else 0
        data.write(Int(flags))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        data.write(self.peer.write())
        
        return data.getvalue()
