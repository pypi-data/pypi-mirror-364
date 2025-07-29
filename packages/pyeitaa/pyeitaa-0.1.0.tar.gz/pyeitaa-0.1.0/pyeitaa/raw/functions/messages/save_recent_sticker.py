from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class SaveRecentSticker(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x392718f8``

    Parameters:
        id: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        unsave: ``bool``
        attached (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id", "unsave", "attached"]

    ID = 0x392718f8
    QUALNAME = "functions.messages.SaveRecentSticker"

    def __init__(self, *, id: "raw.base.InputDocument", unsave: bool, attached: Optional[bool] = None) -> None:
        self.id = id  # InputDocument
        self.unsave = unsave  # Bool
        self.attached = attached  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        attached = True if flags & (1 << 0) else False
        id = TLObject.read(data)
        
        unsave = Bool.read(data)
        
        return SaveRecentSticker(id=id, unsave=unsave, attached=attached)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.attached else 0
        data.write(Int(flags))
        
        data.write(self.id.write())
        
        data.write(Bool(self.unsave))
        
        return data.getvalue()
