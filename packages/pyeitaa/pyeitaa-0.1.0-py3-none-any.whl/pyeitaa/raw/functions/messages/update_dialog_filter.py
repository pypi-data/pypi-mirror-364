from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateDialogFilter(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1ad4a04a``

    Parameters:
        id: ``int`` ``32-bit``
        filter (optional): :obj:`DialogFilter <pyeitaa.raw.base.DialogFilter>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id", "filter"]

    ID = 0x1ad4a04a
    QUALNAME = "functions.messages.UpdateDialogFilter"

    def __init__(self, *, id: int, filter: "raw.base.DialogFilter" = None) -> None:
        self.id = id  # int
        self.filter = filter  # flags.0?DialogFilter

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        id = Int.read(data)
        
        filter = TLObject.read(data) if flags & (1 << 0) else None
        
        return UpdateDialogFilter(id=id, filter=filter)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.filter is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.id))
        
        if self.filter is not None:
            data.write(self.filter.write())
        
        return data.getvalue()
