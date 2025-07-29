from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputChatPhoto(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputChatPhoto`.

    Details:
        - Layer: ``135``
        - ID: ``-0x76ac52c9``

    Parameters:
        id: :obj:`InputPhoto <pyeitaa.raw.base.InputPhoto>`
    """

    __slots__: List[str] = ["id"]

    ID = -0x76ac52c9
    QUALNAME = "types.InputChatPhoto"

    def __init__(self, *, id: "raw.base.InputPhoto") -> None:
        self.id = id  # InputPhoto

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return InputChatPhoto(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()
