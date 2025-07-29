from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputStickeredMediaDocument(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputStickeredMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x438865b``

    Parameters:
        id: :obj:`InputDocument <pyeitaa.raw.base.InputDocument>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x438865b
    QUALNAME = "types.InputStickeredMediaDocument"

    def __init__(self, *, id: "raw.base.InputDocument") -> None:
        self.id = id  # InputDocument

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return InputStickeredMediaDocument(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()
