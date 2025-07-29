from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ReorderStickerSets(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x78337739``

    Parameters:
        order: List of ``int`` ``64-bit``
        masks (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["order", "masks"]

    ID = 0x78337739
    QUALNAME = "functions.messages.ReorderStickerSets"

    def __init__(self, *, order: List[int], masks: Optional[bool] = None) -> None:
        self.order = order  # Vector<long>
        self.masks = masks  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        masks = True if flags & (1 << 0) else False
        order = TLObject.read(data, Long)
        
        return ReorderStickerSets(order=order, masks=masks)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.masks else 0
        data.write(Int(flags))
        
        data.write(Vector(self.order, Long))
        
        return data.getvalue()
