from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdatePinnedDialogs(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5f0c35e``

    Parameters:
        folder_id (optional): ``int`` ``32-bit``
        order (optional): List of :obj:`DialogPeer <pyeitaa.raw.base.DialogPeer>`
    """

    __slots__: List[str] = ["folder_id", "order"]

    ID = -0x5f0c35e
    QUALNAME = "types.UpdatePinnedDialogs"

    def __init__(self, *, folder_id: Optional[int] = None, order: Optional[List["raw.base.DialogPeer"]] = None) -> None:
        self.folder_id = folder_id  # flags.1?int
        self.order = order  # flags.0?Vector<DialogPeer>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        folder_id = Int.read(data) if flags & (1 << 1) else None
        order = TLObject.read(data) if flags & (1 << 0) else []
        
        return UpdatePinnedDialogs(folder_id=folder_id, order=order)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.folder_id is not None else 0
        flags |= (1 << 0) if self.order is not None else 0
        data.write(Int(flags))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        if self.order is not None:
            data.write(Vector(self.order))
        
        return data.getvalue()
