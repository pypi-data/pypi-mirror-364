from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bool
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class FaveSticker(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x46003aa5``

    Parameters:
        id: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
        unfave: ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id", "unfave"]

    ID = -0x46003aa5
    QUALNAME = "functions.messages.FaveSticker"

    def __init__(self, *, id: "raw.base.InputDocument", unfave: bool) -> None:
        self.id = id  # InputDocument
        self.unfave = unfave  # Bool

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        unfave = Bool.read(data)
        
        return FaveSticker(id=id, unfave=unfave)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        data.write(Bool(self.unfave))
        
        return data.getvalue()
