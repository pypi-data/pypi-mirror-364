from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ClearSavedInfo(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x27c28f3f``

    Parameters:
        credentials (optional): ``bool``
        info (optional): ``bool``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["credentials", "info"]

    ID = -0x27c28f3f
    QUALNAME = "functions.payments.ClearSavedInfo"

    def __init__(self, *, credentials: Optional[bool] = None, info: Optional[bool] = None) -> None:
        self.credentials = credentials  # flags.0?true
        self.info = info  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        credentials = True if flags & (1 << 0) else False
        info = True if flags & (1 << 1) else False
        return ClearSavedInfo(credentials=credentials, info=info)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.credentials else 0
        flags |= (1 << 1) if self.info else 0
        data.write(Int(flags))
        
        return data.getvalue()
