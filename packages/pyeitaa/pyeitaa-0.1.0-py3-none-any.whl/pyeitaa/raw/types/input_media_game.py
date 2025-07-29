from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputMediaGame(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputMedia`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2cc0bc0d``

    Parameters:
        id: :obj:`InputGame <pyeitaa.raw.base.InputGame>`
    """

    __slots__: List[str] = ["id"]

    ID = -0x2cc0bc0d
    QUALNAME = "types.InputMediaGame"

    def __init__(self, *, id: "raw.base.InputGame") -> None:
        self.id = id  # InputGame

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return InputMediaGame(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()
