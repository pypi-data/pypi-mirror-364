from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class FinishTakeoutSession(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x1d2652ee``

    Parameters:
        success (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["success"]

    ID = 0x1d2652ee
    QUALNAME = "functions.account.FinishTakeoutSession"

    def __init__(self, *, success: Optional[bool] = None) -> None:
        self.success = success  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        success = True if flags & (1 << 0) else False
        return FinishTakeoutSession(success=success)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.success else 0
        data.write(Int(flags))
        
        return data.getvalue()
