from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ReplyKeyboardMarkup(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ReplyMarkup`.

    Details:
        - Layer: ``135``
        - ID: ``-0x7a22662f``

    Parameters:
        rows: List of :obj:`KeyboardButtonRow <pyeitaa.raw.base.KeyboardButtonRow>`
        resize (optional): ``bool``
        single_use (optional): ``bool``
        selective (optional): ``bool``
        placeholder (optional): ``str``
    """

    __slots__: List[str] = ["rows", "resize", "single_use", "selective", "placeholder"]

    ID = -0x7a22662f
    QUALNAME = "types.ReplyKeyboardMarkup"

    def __init__(self, *, rows: List["raw.base.KeyboardButtonRow"], resize: Optional[bool] = None, single_use: Optional[bool] = None, selective: Optional[bool] = None, placeholder: Optional[str] = None) -> None:
        self.rows = rows  # Vector<KeyboardButtonRow>
        self.resize = resize  # flags.0?true
        self.single_use = single_use  # flags.1?true
        self.selective = selective  # flags.2?true
        self.placeholder = placeholder  # flags.3?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        resize = True if flags & (1 << 0) else False
        single_use = True if flags & (1 << 1) else False
        selective = True if flags & (1 << 2) else False
        rows = TLObject.read(data)
        
        placeholder = String.read(data) if flags & (1 << 3) else None
        return ReplyKeyboardMarkup(rows=rows, resize=resize, single_use=single_use, selective=selective, placeholder=placeholder)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.resize else 0
        flags |= (1 << 1) if self.single_use else 0
        flags |= (1 << 2) if self.selective else 0
        flags |= (1 << 3) if self.placeholder is not None else 0
        data.write(Int(flags))
        
        data.write(Vector(self.rows))
        
        if self.placeholder is not None:
            data.write(String(self.placeholder))
        
        return data.getvalue()
