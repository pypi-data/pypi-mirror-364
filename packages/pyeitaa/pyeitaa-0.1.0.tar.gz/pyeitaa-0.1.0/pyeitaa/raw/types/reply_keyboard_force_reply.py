from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ReplyKeyboardForceReply(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ReplyMarkup`.

    Details:
        - Layer: ``135``
        - ID: ``-0x794bf4f8``

    Parameters:
        single_use (optional): ``bool``
        selective (optional): ``bool``
        placeholder (optional): ``str``
    """

    __slots__: List[str] = ["single_use", "selective", "placeholder"]

    ID = -0x794bf4f8
    QUALNAME = "types.ReplyKeyboardForceReply"

    def __init__(self, *, single_use: Optional[bool] = None, selective: Optional[bool] = None, placeholder: Optional[str] = None) -> None:
        self.single_use = single_use  # flags.1?true
        self.selective = selective  # flags.2?true
        self.placeholder = placeholder  # flags.3?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        single_use = True if flags & (1 << 1) else False
        selective = True if flags & (1 << 2) else False
        placeholder = String.read(data) if flags & (1 << 3) else None
        return ReplyKeyboardForceReply(single_use=single_use, selective=selective, placeholder=placeholder)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.single_use else 0
        flags |= (1 << 2) if self.selective else 0
        flags |= (1 << 3) if self.placeholder is not None else 0
        data.write(Int(flags))
        
        if self.placeholder is not None:
            data.write(String(self.placeholder))
        
        return data.getvalue()
