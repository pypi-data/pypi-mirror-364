from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ClearRecentStickers(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x76669fd3``

    Parameters:
        attached (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["attached"]

    ID = -0x76669fd3
    QUALNAME = "functions.messages.ClearRecentStickers"

    def __init__(self, *, attached: Optional[bool] = None) -> None:
        self.attached = attached  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        attached = True if flags & (1 << 0) else False
        return ClearRecentStickers(attached=attached)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.attached else 0
        data.write(Int(flags))
        
        return data.getvalue()
