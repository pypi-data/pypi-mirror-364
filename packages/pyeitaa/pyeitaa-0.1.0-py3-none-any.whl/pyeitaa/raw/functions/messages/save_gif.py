from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SaveGif(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x327a30cb``

    Parameters:
        id: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        unsave: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id", "unsave"]

    ID = 0x327a30cb
    QUALNAME = "functions.messages.SaveGif"

    def __init__(self, *, id: "raw.base.InputDocument", unsave: bool) -> None:
        self.id = id  # InputDocument
        self.unsave = unsave  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        unsave = Bool.read(data)
        
        return SaveGif(id=id, unsave=unsave)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        data.write(Bool(self.unsave))
        
        return data.getvalue()
