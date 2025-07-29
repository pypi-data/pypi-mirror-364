from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputStickeredMediaPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputStickeredMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x4a992157``

    Parameters:
        id: :obj:`InputPhoto <pyeitaa.raw.base.InputPhoto>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x4a992157
    QUALNAME = "types.InputStickeredMediaPhoto"

    def __init__(self, *, id: "raw.base.InputPhoto") -> None:
        self.id = id  # InputPhoto

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return InputStickeredMediaPhoto(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()
