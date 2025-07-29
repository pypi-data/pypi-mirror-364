from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ReplyKeyboardHide(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ReplyMarkup`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5fc1a47b``

    Parameters:
        selective (optional): ``bool``
    """

    __slots__: List[str] = ["selective"]

    ID = -0x5fc1a47b
    QUALNAME = "types.ReplyKeyboardHide"

    def __init__(self, *, selective: Optional[bool] = None) -> None:
        self.selective = selective  # flags.2?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        selective = True if flags & (1 << 2) else False
        return ReplyKeyboardHide(selective=selective)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 2) if self.selective else 0
        data.write(Int(flags))
        
        return data.getvalue()
