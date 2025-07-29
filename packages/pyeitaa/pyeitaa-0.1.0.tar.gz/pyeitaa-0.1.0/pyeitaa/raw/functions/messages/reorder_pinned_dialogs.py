from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ReorderPinnedDialogs(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3b1adf37``

    Parameters:
        folder_id: ``int`` ``32-bit``
        order: List of :obj:`InputDialogPeer <pyeitaa.raw.base.InputDialogPeer>`
        force (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["folder_id", "order", "force"]

    ID = 0x3b1adf37
    QUALNAME = "functions.messages.ReorderPinnedDialogs"

    def __init__(self, *, folder_id: int, order: List["raw.base.InputDialogPeer"], force: Optional[bool] = None) -> None:
        self.folder_id = folder_id  # int
        self.order = order  # Vector<InputDialogPeer>
        self.force = force  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        force = True if flags & (1 << 0) else False
        folder_id = Int.read(data)
        
        order = TLObject.read(data)
        
        return ReorderPinnedDialogs(folder_id=folder_id, order=order, force=force)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.force else 0
        data.write(Int(flags))
        
        data.write(Int(self.folder_id))
        
        data.write(Vector(self.order))
        
        return data.getvalue()
