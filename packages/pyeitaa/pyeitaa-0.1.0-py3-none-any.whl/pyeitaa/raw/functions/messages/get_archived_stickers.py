from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class GetArchivedStickers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x57f17692``

    Parameters:
        offset_id: ``int`` ``64-bit``
        limit: ``int`` ``32-bit``
        masks (optional): ``bool``

    Returns:
        :obj:`messages.ArchivedStickers <pyeitaa.raw.base.messages.ArchivedStickers>`
    """

    __slots__: List[str] = ["offset_id", "limit", "masks"]

    ID = 0x57f17692
    QUALNAME = "functions.messages.GetArchivedStickers"

    def __init__(self, *, offset_id: int, limit: int, masks: Optional[bool] = None) -> None:
        self.offset_id = offset_id  # long
        self.limit = limit  # int
        self.masks = masks  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        masks = True if flags & (1 << 0) else False
        offset_id = Long.read(data)
        
        limit = Int.read(data)
        
        return GetArchivedStickers(offset_id=offset_id, limit=limit, masks=masks)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.masks else 0
        data.write(Int(flags))
        
        data.write(Long(self.offset_id))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
