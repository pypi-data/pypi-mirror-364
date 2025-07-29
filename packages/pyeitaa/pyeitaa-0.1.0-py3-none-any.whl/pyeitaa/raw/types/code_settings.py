from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class CodeSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.CodeSettings`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2141417d``

    Parameters:
        allow_flashcall (optional): ``bool``
        current_number (optional): ``bool``
        allow_app_hash (optional): ``bool``
    """

    __slots__: List[str] = ["allow_flashcall", "current_number", "allow_app_hash"]

    ID = -0x2141417d
    QUALNAME = "types.CodeSettings"

    def __init__(self, *, allow_flashcall: Optional[bool] = None, current_number: Optional[bool] = None, allow_app_hash: Optional[bool] = None) -> None:
        self.allow_flashcall = allow_flashcall  # flags.0?true
        self.current_number = current_number  # flags.1?true
        self.allow_app_hash = allow_app_hash  # flags.4?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        allow_flashcall = True if flags & (1 << 0) else False
        current_number = True if flags & (1 << 1) else False
        allow_app_hash = True if flags & (1 << 4) else False
        return CodeSettings(allow_flashcall=allow_flashcall, current_number=current_number, allow_app_hash=allow_app_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.allow_flashcall else 0
        flags |= (1 << 1) if self.current_number else 0
        flags |= (1 << 4) if self.allow_app_hash else 0
        data.write(Int(flags))
        
        return data.getvalue()
